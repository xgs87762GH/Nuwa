"""
测试模板系统是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.utils.template import TemplateVariableProcessor, EnhancedPromptTemplates


def test_template_system():
    """测试模板系统"""
    print("🧪 开始测试模板系统...")

    # 初始化模板处理器
    template_dir = str(project_root / "templates" / "prompts")
    processor = TemplateVariableProcessor()
    prompt_templates = EnhancedPromptTemplates(template_dir)

    # 测试1: 全局变量
    print("\n📊 全局变量测试:")
    global_vars = processor.get_global_variables()
    for key, value in global_vars.items():
        print(f"  {key}: {value}")

    # 测试2: 插件选择模板
    print("\n🔌 插件选择模板测试:")
    mock_plugins = [
        {
            'plugin_name': 'Camera Plugin',
            'description': '相机控制插件',
            'tags': ['camera', 'photo'],
            'functions': [
                {'name': 'take_photo', 'description': '拍摄照片'},
                {'name': 'record_video', 'description': '录制视频'}
            ]
        }
    ]

    try:
        plugin_prompt = prompt_templates.get_plugin_selection_prompt(mock_plugins)
        print("✅ 插件选择模板渲染成功")
        print(f"模板长度: {len(plugin_prompt)} 字符")
        print("模板预览:")
        print("=" * 50)
        print(plugin_prompt[:500] + "..." if len(plugin_prompt) > 500 else plugin_prompt)
        print("=" * 50)
    except Exception as e:
        print(f"❌ 插件选择模板渲染失败: {e}")

    # 测试3: 执行计划模板
    print("\n📋 执行计划模板测试:")
    mock_selected_plugins = [
        {'plugin_name': 'Camera Plugin', 'plugin_id': 'camera', 'reason': '用户需要拍照'}
    ]

    try:
        plan_prompt = prompt_templates.get_execution_plan_prompt(
            mock_selected_plugins, "帮我拍一张照片"
        )
        print("✅ 执行计划模板渲染成功")
        print(f"模板长度: {len(plan_prompt)} 字符")
    except Exception as e:
        print(f"❌ 执行计划模板渲染失败: {e}")

    # 测试4: 结果总结模板
    print("\n📝 结果总结模板测试:")
    mock_results = [
        {'step': 1, 'status': 'success', 'description': '拍照成功'}
    ]

    try:
        summary_prompt = prompt_templates.get_result_summary_prompt(
            mock_results, "帮我拍一张照片"
        )
        print("✅ 结果总结模板渲染成功")
        print(f"模板长度: {len(summary_prompt)} 字符")
    except Exception as e:
        print(f"❌ 结果总结模板渲染失败: {e}")

    print("\n🎉 模板系统测试完成!")


if __name__ == "__main__":
    test_template_system()
