import asyncio
import time
from typing import List

from src.core.plugin import PluginManager
from src.core.tasks.model.response import TaskStepResponse, TaskResponse, StepExecutionResult


class TaskExecutor:
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager

    async def execute(self, task: TaskResponse) -> List[StepExecutionResult]:
        """
        执行执行计划中的所有插件方法
        返回每个步骤的结构化执行结果 StepExecutionResult 列表
        """
        results: List[StepExecutionResult] = []
        steps: List[TaskStepResponse] = task.steps

        for step in steps:
            start_ts = time.time()
            try:
                function_name = step.function_name
                plugin_id = step.plugin_id
                params = step.params or {}
                plugin_name = step.plugin_name

                # 通过 PluginManager 的统一入口调用，避免直接访问注册对象
                if hasattr(self.plugin_manager, "call"):
                    if asyncio.iscoroutinefunction(self.plugin_manager.call):
                        result = await self.plugin_manager.call(plugin_id, function_name, **params)
                    else:
                        # 兼容同步实现
                        result = self.plugin_manager.call(plugin_id, function_name, **params)
                else:
                    raise AttributeError("PluginManager does not have a 'call' method")

                duration_ms = int((time.time() - start_ts) * 1000)
                results.append(StepExecutionResult(
                    step_id=step.step_id,
                    plugin_id=plugin_id,
                    plugin_name=plugin_name,
                    function_name=function_name,
                    params=params,
                    result=result,
                    success=True,
                    started_at=None,
                    finished_at=None,
                    duration_ms=duration_ms
                ))

            except Exception as e:
                duration_ms = int((time.time() - start_ts) * 1000)
                results.append(StepExecutionResult(
                    step_id=getattr(step, 'step_id', None),
                    plugin_id=getattr(step, 'plugin_id', ''),
                    plugin_name=getattr(step, 'plugin_name', None),
                    function_name=getattr(step, 'function_name', ''),
                    params=getattr(step, 'params', {}) or {},
                    result=None,
                    success=False,
                    error=str(e),
                    started_at=None,
                    finished_at=None,
                    duration_ms=duration_ms
                ))
        return results
