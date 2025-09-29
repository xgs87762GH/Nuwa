import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy import select, func, delete, desc, asc
from sqlalchemy.orm import selectinload

from src.core.config import DataBaseManager, get_logger
from src.core.orchestration import IntelligentPluginRouter
from src.core.orchestration.model import PlanResult
from src.core.tasks.model.models import Task, TaskStatus
from src.core.tasks.model.response import TaskQuery, PaginatedTaskResponse, TaskResponse, TaskDetailResponse
from src.core.tasks.service_step import TaskStepService

logger = get_logger(__name__)


class TaskService:
    def __init__(self, db: DataBaseManager, step_service: TaskStepService):
        self.db = db
        self.step_service = step_service

    async def create_task_from_input(self, user_input: str, router: IntelligentPluginRouter, user_id: str = "1") -> \
            Dict[str, Any]:
        """
        Create a task from user input

        1. Call IntelligentPluginRouter to get the orchestration plan
        2. Save Task to the database
        3. Return the task information
        """
        try:
            # 1. Generate orchestration plan
            plan_result: PlanResult = await router.analyze_and_plan(user_input)
            if not plan_result.success:
                logger.warning(f"Plan generation failed: {plan_result.error}")
                return {
                    "success": False,
                    "error": plan_result.error or "Plan generation failed",
                    "plan_result": plan_result.__dict__
                }

            task_id = str(uuid.uuid4())
            current_time = datetime.now(timezone.utc)

            # 2. Construct Task object
            task = Task(
                task_id=task_id,
                user_id=user_id,
                description=plan_result.user_input or user_input,
                status=TaskStatus.PENDING,
                execution_plan=plan_result.execution_plan.to_dict() if plan_result.execution_plan else None,
                extra={
                    "selected_plugins": plan_result.selected_plugins_to_dict() or []
                },
                created_at=current_time,
                scheduled_at=current_time
            )

            # 3. Save to database
            async with self.db.get_session() as session:
                session.add(task)
                # Create steps using TaskStepService
                step_count = await self.step_service.create_steps_for_task(session, task_id, plan_result.execution_plan)
                await session.commit()

            logger.info(f"Task {task_id} created successfully with {step_count} steps")
            return {"success": True, "task_id": task_id, "step_count": step_count}

        except Exception as e:
            logger.error(f"Failed to create task from input '{user_input}': {e}")
            logger.exception(e)
            return {
                "success": False,
                "error": f"Failed to create task: {str(e)}",
                "plan_result": plan_result.__dict__ if 'plan_result' in locals() else None
            }

    async def query_tasks(self, query: TaskQuery) -> PaginatedTaskResponse:
        async with self.db.get_session() as session:
            # 1. Base statement
            stmt = select(Task).options(selectinload(Task.steps))

            # 2. Dynamic filters
            if query.task_id:
                stmt = stmt.where(Task.task_id == query.task_id)
            if query.description:
                stmt = stmt.where(Task.description.contains(query.description))
            if query.status:
                stmt = stmt.where(Task.status == query.status)

            # 3. Dynamic ordering
            order_columns = []
            for sf in query.sorts:
                col = getattr(Task, sf.field)  # Get column
                order_columns.append(
                    desc(col) if sf.order == "desc" else asc(col)
                )
            stmt = stmt.order_by(*order_columns)

            # 4. Total count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = (await session.execute(count_stmt)).scalar_one()

            # 5. Pagination
            stmt = stmt.offset((query.page - 1) * query.size).limit(query.size)
            tasks = (await session.execute(stmt)).scalars().all()

            # 6. Serialize and return
            items = [TaskResponse.model_validate(t, from_attributes=True) for t in tasks]
            return PaginatedTaskResponse(
                total=total, page=query.page, size=query.size, items=items
            )

    async def get_task_detail(self, task_id: str) -> Optional[TaskDetailResponse]:
        """Get detailed information of a single task, including steps and plan/result fields."""
        if not task_id:
            raise ValueError("task_id cannot be empty")

        async with self.db.get_session() as session:
            stmt = (
                select(Task)
                .options(selectinload(Task.steps))
                .where(Task.task_id == task_id)
            )
            result = await session.execute(stmt)
            task: Optional[Task] = result.scalar_one_or_none()
            if not task:
                return None

            # Pydantic v2 conversion from ORM object with relationships
            detail = TaskDetailResponse.model_validate(task, from_attributes=True)
            return detail

    async def del_task(self, task_id: str):
        """删除任务"""
        if not task_id:
            raise ValueError("task_id cannot be empty")

        try:
            async with self.db.get_session() as session:
                result = await session.execute(
                    delete(Task).where(Task.task_id == task_id)
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            raise

    async def update_task_fields(self, task_id: str, **kwargs) -> Optional[Task]:
        """Update specific fields of a task"""
        if not task_id:
            raise ValueError("task_id cannot be empty")

        async with self.db.get_session() as session:
            try:
                stmt = select(Task).where(
                    Task.task_id == task_id
                )
                result = await session.execute(stmt)
                task = result.scalar_one_or_none()

                if not task:
                    raise ValueError(f"Task {task_id} not found")

                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)

                await session.commit()
                await session.refresh(task)
                logger.info(f"Task {task_id} updated successfully")
                return task
            except Exception as e:
                logger.error(f"Failed to update task {task_id}: {str(e)}")
                raise
