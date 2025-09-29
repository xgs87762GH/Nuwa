import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.ai.providers.response import ExecutionPlan
from src.core.config import DataBaseManager, get_logger
from src.core.tasks.model.models import TaskStep, TaskStatus

logger = get_logger(__name__)


class StepHandler:
    def __init__(self, db: DataBaseManager):
        self.db = db

    async def create_steps_for_task(self, session: AsyncSession, task_id: str, execution_plan: ExecutionPlan):
        """
        Based on the execution plan, create all steps for the task.
        """
        if not execution_plan:
            return 0

        execution_functions = execution_plan.get_ordered_functions()
        if not execution_functions:
            return 0

        for idx, function_selection in enumerate(execution_functions):
            step_id = f"{task_id}_{idx + 1}"
            task_step = TaskStep(
                step_id=step_id,
                task_id=task_id,
                plugin_id=function_selection.plugin_id,
                plugin_name=function_selection.plugin_name,
                function_name=function_selection.function_name,
                params=function_selection.suggested_params or {},
                status=TaskStatus.PENDING
            )
            session.add(task_step)

        step_count = len(execution_functions)
        logger.info(f"Prepared {step_count} steps for task {task_id}")
        return step_count

    async def update_step_fields(self, step_id: str, **kwargs):
        """Update specific fields of a task step"""
        async with self.db.get_session() as session:
            try:
                stmt = select(TaskStep).where(
                    TaskStep.step_id == step_id
                )
                result = await session.execute(stmt)
                task_step = result.scalar_one_or_none()

                if not task_step:
                    raise ValueError(f"Task step {step_id} not found")

                for key, value in kwargs.items():
                    if hasattr(task_step, key):
                        setattr(task_step, key, value)

                await session.commit()
                await session.refresh(task_step)
                logger.info(f"Task step {step_id} updated successfully")
                return task_step
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating task step {step_id}: {str(e)}")
                raise
