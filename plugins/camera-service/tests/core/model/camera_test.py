from core.exceptions import ValidationError
from model import CameraParameterBase


def example_usage():
    # 创建参数对象
    camera_params = CameraParameterBase(
        camera_id=0,
        width=1920,
        height=1080,
        brightness=0.2
    )

    # 查看参数信息
    param_info = camera_params.get_parameter_info()
    print("Parameter info:", param_info['brightness'])
    # 输出: {'type': 'Optional[float]', 'default': None, 'description': 'Brightness adjustment', 'range': (-1.0, 1.0), 'validator': 'range'}

    # 查看所有范围
    ranges = camera_params.get_parameter_ranges()
    print("Parameter ranges:", ranges)
    # 输出: {'width': (160, 7680), 'height': (120, 4320), 'brightness': (-1.0, 1.0), ...}

    # 更新参数（自动验证）
    result = camera_params.update_parameters(
        brightness=0.5,  # ✅ 有效
        gain=1.5,  # ❌ 超出范围
        unknown_param=123  # ❌ 未知参数
    )

    print("Update result:", result)
    # 输出: {
    #   'changes': {'brightness': {'old': 0.2, 'new': 0.5}},
    #   'errors': {
    #     'gain': 'Invalid gain: gain must be between 0.0 and 1.0',
    #     'unknown_param': 'Unknown parameter: unknown_param'
    #   }
    # }

    # 单个参数验证
    try:
        camera_params.validate_single_parameter('fps', 150.0)
    except ValidationError as e:
        print(f"Validation error: {e}")
        # 输出: Validation error: Invalid fps: fps must be between 1.0 and 120.0


if __name__ == "__main__":
    example_usage()
