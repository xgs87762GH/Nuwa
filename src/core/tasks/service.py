import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from src.core.ai.providers.response import ExecutionPlan
from src.core.config import DataBaseManager, get_logger
from src.core.orchestration import IntelligentPluginRouter
from src.core.orchestration.model import PlanResult
from src.core.tasks.model.models import Task, TaskStep, TaskStatus
from src.core.tasks.model.response import TaskQuery, PaginatedTaskResponse, TaskResponse, TaskDetailResponse

logger = get_logger(__name__)


class TaskService:
    def __init__(self, db: DataBaseManager):
        self.db = db

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

            # 3. Create task steps
            execution_plan: ExecutionPlan = plan_result.execution_plan
            if execution_plan:
                execution_functions = execution_plan.get_ordered_functions()
                if execution_functions:
                    for idx, function_selection in enumerate(execution_functions):
                        step_id = f"{task_id}_{idx + 1}"
                        task_step = TaskStep(
                            step_id=step_id,
                            task_id=task_id,  # Explicitly set task_id
                            plugin_id=function_selection.plugin_id,
                            plugin_name=function_selection.plugin_name,
                            function_name=function_selection.function_name,
                            params=function_selection.suggested_params or {},
                            status=TaskStatus.PENDING
                        )
                        task.add_step(task_step)

            # 4. Save to database
            async with self.db.get_session() as session:
                session.add(task)
                await session.commit()

            logger.info(f"Task {task_id} created successfully with {len(task.steps)} steps")
            return {"success": True, "task_id": task_id, "step_count": len(task.steps)}

        except Exception as e:
            logger.error(f"Failed to create task from input '{user_input}': {e}")
            logger.exception(e)
            return {
                "success": False,
                "error": f"Failed to create task: {str(e)}",
                "plan_result": plan_result.__dict__ if 'plan_result' in locals() else None
            }

    async def query_tasks(self, query: TaskQuery) -> PaginatedTaskResponse:
        """
        Paginated query for tasks based on criteria.
        """
        async with self.db.get_session() as session:
            # 基础查询，并预加载 steps 关系以避免 N+1 问题
            stmt = select(Task).options(selectinload(Task.steps))

            # 根据查询参数动态添加过滤条件
            if query.task_id:
                stmt = stmt.where(Task.task_id == query.task_id)
            if query.description:
                stmt = stmt.where(Task.description.contains(query.description))
            if query.status:
                stmt = stmt.where(Task.status == query.status)

            # 获取总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = (await session.execute(count_stmt)).scalar_one()

            # 添加排序、分页
            stmt = stmt.order_by(Task.created_at.desc()) \
                .offset((query.page - 1) * query.size) \
                .limit(query.size)

            # 执行查询
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            # 将 SQLAlchemy 模型转换为 Pydantic 模型
            task_responses = [TaskResponse.model_validate(task, from_attributes=True) for task in tasks]

            # 封装并返回 Pydantic 模型
            return PaginatedTaskResponse(
                total=total,
                page=query.page,
                size=query.size,
                items=task_responses
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
