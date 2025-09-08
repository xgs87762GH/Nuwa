import asyncio


class PluginExecutor:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager

    async def execute(self, execution_plan):
        """
        执行执行计划中的所有插件方法
        execution_plan: ExecutionPlan 或 dict, 包含步骤列表
        返回各步骤执行结果
        """
        results = []
        steps = getattr(execution_plan, "selected_functions", None) or execution_plan.get("selected_functions", [])

        for step in steps:
            try:
                plugin_id = step.get("plugin_id")
                function_name = step.get("function_name")
                params = step.get("params", {})

                plugin = await self.plugin_manager.get_register_plugin(plugin_id)
                func = getattr(plugin, function_name, None)
                if not func:
                    raise Exception(f"插件 {plugin_id} 未找到方法 {function_name}")

                # 支持异步和同步
                if hasattr(func, "__call__"):
                    if asyncio.iscoroutinefunction(func):
                        result = await func(**params)
                    else:
                        result = func(**params)
                else:
                    result = None

                results.append({
                    "plugin_id": plugin_id,
                    "function_name": function_name,
                    "params": params,
                    "result": result,
                    "success": True
                })

            except Exception as e:
                results.append({
                    "plugin_id": step.get("plugin_id"),
                    "function_name": step.get("function_name"),
                    "params": step.get("params", {}),
                    "result": str(e),
                    "success": False
                })
        return results
# Task Executor Module

