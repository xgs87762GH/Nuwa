"""
Plugin Module Import Rewriter
Handles dynamic rewriting of import statements in plugin modules
"""
import importlib.util
import os
import tempfile
from pathlib import Path

from src.core.config import get_logger

logger = get_logger("module_rewriter")


class PluginModuleRewriter:
    """Dynamically rewrite import statements in plugin modules"""

    def __init__(self, plugin_dir: Path, module_prefix: str):
        self.plugin_dir = plugin_dir
        self.module_prefix = module_prefix

    def rewrite_imports_and_load(self, file_path: Path, module_name: str):
        """Rewrite import statements and load module"""
        try:
            # Read original file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Rewrite import statements
            rewritten_content = self._rewrite_import_statements(original_content)

            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(rewritten_content)
                temp_file_path = temp_file.name

            try:
                # Load module from temporary file
                spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        except Exception as e:
            # If rewriting fails, try loading original file directly
            logger.warning(f"Failed to rewrite imports, attempting direct load: {e}")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

    def _rewrite_import_statements(self, content: str) -> str:
        """Rewrite import statements to redirect local imports to plugin namespace"""
        lines = content.split('\n')
        rewritten_lines = []

        for line in lines:
            stripped = line.strip()

            # Handle 'from xxx import yyy' style imports
            if stripped.startswith('from ') and ' import ' in stripped:
                rewritten_line = self._rewrite_from_import(line)
                rewritten_lines.append(rewritten_line)

            # Handle 'import xxx' style imports
            elif stripped.startswith('import ') and not stripped.startswith('import os') and not stripped.startswith(
                    'import sys'):
                rewritten_line = self._rewrite_import(line)
                rewritten_lines.append(rewritten_line)

            else:
                rewritten_lines.append(line)

        return '\n'.join(rewritten_lines)

    def _rewrite_from_import(self, line: str) -> str:
        """Rewrite 'from xxx import yyy' statements"""
        # Check if it's a relative import
        if 'from .' in line:
            return line  # Keep relative imports unchanged

        # Check if it's a local module import
        parts = line.strip().split()
        if len(parts) >= 4 and parts[0] == 'from':
            module_name = parts[1]

            # Check if it's a module within the plugin
            if self._is_local_module(module_name):
                # Try to add plugin prefix
                return line.replace(f'from {module_name}', f'from {self.module_prefix}.{module_name}', 1)

        return line

    def _rewrite_import(self, line: str) -> str:
        """Rewrite 'import xxx' statements"""
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0] == 'import':
            module_name = parts[1]

            # Check if it's a module within the plugin
            if self._is_local_module(module_name):
                return line.replace(f'import {module_name}',
                                    f'import {self.module_prefix}.{module_name} as {module_name}', 1)

        return line

    def _is_local_module(self, module_name: str) -> bool:
        """Check if it's a local module within the plugin"""
        if not module_name or '.' in module_name:
            return False

        # Check if corresponding module file/directory exists in plugin directory
        potential_paths = [
            self.plugin_dir / f"{module_name}.py",
            self.plugin_dir / module_name / "__init__.py"
        ]

        return any(path.exists() for path in potential_paths)
