# Task Scheduler Module
from abc import ABC

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.core.ai.providers.base import BaseIterator
from src.core.config import get_logger
from src.core.scheduler.task_scheduler import TaskScheduler

LOGGER = get_logger(__name__)


class SchedulerRegister:

    def __init__(self):
        super().__init__()
        self.scheduler = AsyncIOScheduler()
        self._setup_scheduler()

    def _setup_scheduler(self):
        """设置调度器"""

        self.task_executor = TaskScheduler()
        self.scheduler.add_job(
            self.task_executor.execute,
            trigger=IntervalTrigger(seconds=5),
            id='execute_tasks',
            replace_existing=True
        )

    async def start(self):
        """启动调度器"""
        self.scheduler.start()
        LOGGER.info("Task scheduler started")

    async def stop(self):
        """停止调度器"""
        self.scheduler.shutdown(wait=True)
        LOGGER.info("Task scheduler stopped")
