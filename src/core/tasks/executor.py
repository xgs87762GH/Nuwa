import datetime
import time
from typing import List

from src.core.config import get_logger
from src.core.plugin import PluginManager
from src.core.plugin.model import PluginRegistration
from src.core.tasks.model.response import TaskStepResponse, TaskResponse, StepExecutionResult
from src.core.utils.Result import Result
from src.core.utils.time_utils import TimeUtils

LOGGER = get_logger(__name__)


class TaskExecutor:
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager

    async def execute(self, task: TaskResponse) -> List[StepExecutionResult]:
        """
        执行执行计划中的所有插件方法
        返回每个步骤的结果：使用 Result 进行统一成功/失败封装，value 为 StepExecutionResult
        """
        results: List[StepExecutionResult] = []
        steps: List[TaskStepResponse] = task.steps

        for step in steps:
            start_time = TimeUtils.get_current_time()
            try:
                function_name = step.function_name
                plugin_id = step.plugin_id
                params = step.params or {}
                plugin_name = step.plugin_name

                plugin: PluginRegistration = await self.plugin_manager.get_plugin_by_id(plugin_id)
                if plugin is None:
                    plugin = await self.plugin_manager.get_plugin_by_name(plugin_name)
                    plugin_id = plugin.id if plugin else plugin_id

                # 通过 PluginManager 的统一入口调用，避免直接访问注册对象
                result: Result = await self.plugin_manager.call(plugin_id, function_name, **params)

                duration_ms = int((TimeUtils.get_current_time().timestamp() - start_time.timestamp()) * 1000)
                step_result = StepExecutionResult(
                    step_id=step.step_id,
                    plugin_id=plugin_id,
                    plugin_name=plugin_name,
                    function_name=function_name,
                    params=params,
                    success=True,
                    result=result.value,
                    started_at=start_time,
                    finished_at=TimeUtils.get_current_time(),
                    duration_ms=duration_ms
                )
                results.append(step_result)

            except Exception as e:
                duration_ms = int((TimeUtils.get_current_time().timestamp() - start_time.timestamp()) * 1000)
                step_result = StepExecutionResult(
                    step_id=getattr(step, 'step_id', None),
                    plugin_id=getattr(step, 'plugin_id', ''),
                    plugin_name=getattr(step, 'plugin_name', None),
                    function_name=getattr(step, 'function_name', ''),
                    params=getattr(step, 'params', {}) or {},
                    result=None,
                    success=False,
                    error=str(e),
                    started_at=start_time,
                    finished_at=TimeUtils.get_current_time(),
                    duration_ms=duration_ms
                )
                results.append(step_result)
        return results
