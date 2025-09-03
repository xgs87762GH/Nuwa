"""
模板文件管理类 - 负责模板文件读取、缓存、列举等
"""

import os
from pathlib import Path
from typing import Optional, List

class TemplateManager:
    """模板文件管理器"""
    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self._template_cache = {}
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def load_template(self, template_name: str) -> Optional[str]:
        """
        读取模板文件内容
        """
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        template_file = self.template_dir / f"{template_name}.template"
        if not template_file.exists():
            return None
        content = template_file.read_text(encoding='utf-8')
        self._template_cache[template_name] = content
        return content

    def list_templates(self) -> List[str]:
        """
        列出所有可用模板名（不含后缀）
        """
        return [f.stem for f in self.template_dir.glob("*.template")]

    def clear_cache(self):
        self._template_cache.clear()

