# Task Scheduler Module
from datetime import datetime, timezone
from typing import List

from src.core.ai.providers.base import BaseIterator
from src.core.config import get_logger
from src.core.di import container
from src.core.plugin import PluginManager
from src.core.tasks import TaskHandler, TaskExecutor, StepHandler
from src.core.tasks.model.models import TaskStatus
from src.core.tasks.model.response import TaskQuery, TaskResponse, PaginatedTaskResponse, StepExecutionResult, SortField
from src.core.utils.time_utils import TimeUtils

LOGGER = get_logger(__name__)


class TaskIterator(BaseIterator):

    def __init__(self):
        super().__init__()
        self.task_service = container.get(TaskHandler)

    async def query(self) -> List[TaskResponse]:
        """Query the task list"""
        query_param = TaskQuery(
            status=TaskStatus.PENDING,
            page=self.page,
            size=self.size,
            sorts=[
                SortField(field="priority", order="desc"),
                SortField(field="created_at", order="asc")
            ]
        )
        tasks: PaginatedTaskResponse = await self.task_service.query_tasks(query_param)
        return tasks.items if tasks else []


class TaskScheduler:
    def __init__(self):
        self.plugin_manager = container.get(PluginManager)
        self.task_service = container.get(TaskHandler)
        self.step_service = container.get(StepHandler)

    async def execute(self):
        iterator = TaskIterator()
        executor = TaskExecutor(self.plugin_manager)
        """执行任务"""
        while await iterator.hasNext():
            task: TaskResponse = iterator.next()
            LOGGER.info(f"Executing task: {task.task_id}")

            # 1. 标记任务开始执行
            await self.task_service.update_task_fields(
                task.task_id,
                status=TaskStatus.RUNNING,
                started_at=TimeUtils.get_current_time()
            )

            # 2. 执行任务
            LOGGER.info(f"Task description: {task.description}")
            step_results: List[StepExecutionResult] = await executor.execute(task=task)
            LOGGER.info(f"Task {task.task_id} execution completed with {len(step_results)} steps.")

            # 3. 更新所有步骤的状态
            for step_res in step_results:
                step_status = TaskStatus.SUCCESS if step_res.success else TaskStatus.FAILED
                LOGGER.info(f"Step {step_res.step_id} execution completed with status {step_status.value}.")
                LOGGER.info(f"step result: {step_res}")

                await self.step_service.update_step_fields(
                    step_res.step_id,
                    status=step_status,
                    result=step_res.result,
                    error=step_res.error,
                    started_at=step_res.started_at,
                    finished_at=step_res.finished_at
                )

            # 4. 标记任务最终状态
            task_successful = all(step_res.success for step_res in step_results)
            final_status = TaskStatus.SUCCESS if task_successful else TaskStatus.FAILED
            await self.task_service.update_task_fields(
                task.task_id,
                status=final_status,
                result=[res.model_dump(mode='json') for res in step_results],
                finished_at=TimeUtils.get_current_time()
            )
            LOGGER.info(f"Task {task.task_id} finished with status: {final_status.value}")
