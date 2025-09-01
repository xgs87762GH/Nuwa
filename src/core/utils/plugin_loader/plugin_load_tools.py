

import importlib.util
import os
import sys
import tempfile
import threading
import uuid
from pathlib import Path


class PluginEnvironment:
    """为每个插件创建隔离的运行环境"""

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.plugin_name = plugin_dir.name
        self.original_modules = {}
        self.original_path = []
        self.module_prefix = f"plugin_{self.plugin_name.replace('-', '_')}_{uuid.uuid4().hex[:8]}"
        self.lock = threading.Lock()

    def __enter__(self):
        """进入插件环境"""
        with self.lock:
            # 保存当前环境
            self.original_modules = sys.modules.copy()
            self.original_path = sys.path.copy()

            # 设置插件专用的模块搜索路径
            plugin_path = str(self.plugin_dir.resolve())

            # 清理可能冲突的模块
            self._backup_conflicting_modules()

            # 将插件目录添加到搜索路径的最前面
            sys.path.insert(0, plugin_path)

            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出插件环境，恢复原始状态"""
        with self.lock:
            # 恢复原始模块和路径
            sys.modules.clear()
            sys.modules.update(self.original_modules)
            sys.path.clear()
            sys.path.extend(self.original_path)

    def _backup_conflicting_modules(self):
        """备份可能冲突的模块"""
        # 常见的容易冲突的模块名
        potential_conflicts = ['model', 'models', 'services', 'interface', 'utils', 'core', 'config', 'api']

        for module_name in potential_conflicts:
            if module_name in sys.modules:
                # 临时移除这些模块，让插件可以导入自己的版本
                backup_name = f"_backup_{module_name}_{id(self)}"
                sys.modules[backup_name] = sys.modules[module_name]
                del sys.modules[module_name]


class PluginModuleRewriter:
    """动态重写插件模块的导入语句"""

    def __init__(self, plugin_dir: Path, module_prefix: str):
        self.plugin_dir = plugin_dir
        self.module_prefix = module_prefix

    def rewrite_imports_and_load(self, file_path: Path, module_name: str):
        """重写导入语句并加载模块"""
        try:
            # 读取原始文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # 重写导入语句
            rewritten_content = self._rewrite_import_statements(original_content)

            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(rewritten_content)
                temp_file_path = temp_file.name

            try:
                # 从临时文件加载模块
                spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        except Exception as e:
            # 如果重写失败，尝试直接加载原始文件
            print(f"重写导入失败，尝试直接加载: {e}")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

    def _rewrite_import_statements(self, content: str) -> str:
        """重写导入语句，将本地导入重定向到插件命名空间"""
        lines = content.split('\n')
        rewritten_lines = []

        for line in lines:
            stripped = line.strip()

            # 处理 from xxx import yyy 形式的导入
            if stripped.startswith('from ') and ' import ' in stripped:
                rewritten_line = self._rewrite_from_import(line)
                rewritten_lines.append(rewritten_line)

            # 处理 import xxx 形式的导入
            elif stripped.startswith('import ') and not stripped.startswith('import os') and not stripped.startswith(
                    'import sys'):
                rewritten_line = self._rewrite_import(line)
                rewritten_lines.append(rewritten_line)

            else:
                rewritten_lines.append(line)

        return '\n'.join(rewritten_lines)

    def _rewrite_from_import(self, line: str) -> str:
        """重写 from xxx import yyy 语句"""
        # 检查是否是相对导入
        if 'from .' in line:
            return line  # 相对导入保持不变

        # 检查是否是本地模块导入
        parts = line.strip().split()
        if len(parts) >= 4 and parts[0] == 'from':
            module_name = parts[1]

            # 检查是否是插件内的模块
            if self._is_local_module(module_name):
                # 尝试添加插件前缀
                return line.replace(f'from {module_name}', f'from {self.module_prefix}.{module_name}', 1)

        return line

    def _rewrite_import(self, line: str) -> str:
        """重写 import xxx 语句"""
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0] == 'import':
            module_name = parts[1]

            # 检查是否是插件内的模块
            if self._is_local_module(module_name):
                return line.replace(f'import {module_name}',
                                    f'import {self.module_prefix}.{module_name} as {module_name}', 1)

        return line

    def _is_local_module(self, module_name: str) -> bool:
        """检查是否是插件内的本地模块"""
        if not module_name or '.' in module_name:
            return False

        # 检查插件目录中是否存在对应的模块文件/目录
        potential_paths = [
            self.plugin_dir / f"{module_name}.py",
            self.plugin_dir / module_name / "__init__.py"
        ]

        return any(path.exists() for path in potential_paths)
