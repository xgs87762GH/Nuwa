import inspect
from typing import Dict, Type, Any, TypeVar

T = TypeVar('T')


class DIContainer:
    """依赖注入容器"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._type_mappings: Dict[Type, str] = {}

    def register_singleton(self, interface: Type[T], implementation: T) -> None:
        """注册单例服务"""
        key = self._get_key(interface)
        self._singletons[key] = implementation
        self._type_mappings[interface] = key

    def register_factory(self, interface: Type[T], factory: callable) -> None:
        """注册工厂方法"""
        key = self._get_key(interface)
        self._factories[key] = factory
        self._type_mappings[interface] = key

    def register_transient(self, interface: Type[T], implementation_class: Type[T]) -> None:
        """注册瞬时服务（每次获取都创建新实例）"""
        key = self._get_key(interface)
        self._factories[key] = lambda: self._create_instance(implementation_class)
        self._type_mappings[interface] = key

    def get(self, interface: Type[T]) -> T:
        """获取服务实例"""
        key = self._get_key(interface)

        # 优先返回单例
        if key in self._singletons:
            return self._singletons[key]

        # 使用工厂创建
        if key in self._factories:
            return self._factories[key]()

        # 尝试自动创建（如果没有注册但类可以实例化）
        if inspect.isclass(interface):
            try:
                return self._create_instance(interface)
            except Exception:
                pass

        raise ValueError(f"Service {interface.__name__} not registered")

    def _get_key(self, interface: Type) -> str:
        """获取服务的键名"""
        return f"{interface.__module__}.{interface.__name__}"

    def _create_instance(self, cls: Type[T]) -> T:
        """自动创建实例（支持构造函数注入）"""
        # 获取构造函数参数
        sig = inspect.signature(cls.__init__)
        params = {}

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            # 如果参数有类型注解，尝试从容器中获取
            if param.annotation != inspect.Parameter.empty:
                try:
                    params[param_name] = self.get(param.annotation)
                except ValueError:
                    # 如果有默认值，使用默认值
                    if param.default != inspect.Parameter.empty:
                        params[param_name] = param.default
                    else:
                        raise ValueError(f"Cannot resolve dependency {param.annotation} for {cls.__name__}")

        return cls(**params)

    def clear(self) -> None:
        """清空容器"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._type_mappings.clear()


# 全局容器实例
container = DIContainer()