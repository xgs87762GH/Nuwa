# Task Scheduler Module
from typing import List

from src.core.ai.providers.base import BaseIterator
from src.core.config import get_logger
from src.core.di import container
from src.core.plugin import PluginManager
from src.core.tasks import TaskService, TaskExecutor
from src.core.tasks.model.models import TaskStatus
from src.core.tasks.model.response import TaskQuery, TaskResponse, PaginatedTaskResponse

LOGGER = get_logger(__name__)


class TaskIterator(BaseIterator):

    def __init__(self):
        super().__init__()
        self.task_service = container.get(TaskService)

    async def query(self) -> List[TaskResponse]:
        """Query the task list"""
        query_param = TaskQuery(
            status=TaskStatus.PENDING,
            page=self.page,
            size=self.size
        )
        tasks: PaginatedTaskResponse = await self.task_service.query_tasks(query_param)
        return tasks.items if tasks else []


class TaskScheduler:
    def __init__(self):
        self.plugin_manager = container.get(PluginManager)

    async def execute(self):
        iterator = TaskIterator()
        executor = TaskExecutor(self.plugin_manager)
        """执行任务"""
        while await iterator.hasNext():
            task: TaskResponse = iterator.next()
            LOGGER.info(f"Executing task: {task.task_id}")
            LOGGER.info(f"Task description: {task.description}")
            await executor.execute(task=task)
