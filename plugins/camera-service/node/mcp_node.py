# """
# 优化的相机服务 MCP 节点实现 - 统一返回参数结构
# """
#
# import logging
# import time
# import uuid
# from datetime import datetime
# from typing import Dict, Any, Optional
#
# from model import (
#     MCPNode, MCPService,
#     MCPFunction, MCPParameter,
#     CameraParameterBase, PhotoParameters, VideoParameters
# )
# from services.camera_service import CameraService
#
# logger_handler = logging.getLogger(__name__)
#
#
# class CameraMCPNode(MCPNode):
#     """相机服务 MCP 节点 - 统一返回结构"""
#
#     @classmethod
#     def get_service_definition(cls) -> MCPService:
#         """定义相机服务 - 统一返回结构 Schema"""
#
#         # 定义统一的返回结构模板
#         unified_return_schema = {
#             "type": "object",
#             "properties": {
#                 # 核心状态字段
#                 "status": {
#                     "type": "string",
#                     "enum": ["success", "error", "warning"],
#                     "description": "操作执行状态"
#                 },
#                 "success": {
#                     "type": "boolean",
#                     "description": "操作是否成功"
#                 },
#
#                 # 数据载荷
#                 "data": {
#                     "type": "object",
#                     "description": "操作返回的核心数据"
#                 },
#
#                 # 错误信息
#                 "error": {
#                     "type": "object",
#                     "properties": {
#                         "code": {"type": "string", "description": "错误代码"},
#                         "message": {"type": "string", "description": "错误消息"},
#                         "details": {"type": "object", "description": "错误详情"}
#                     },
#                     "description": "错误信息（仅在失败时存在）"
#                 },
#
#                 # 元数据
#                 "metadata": {
#                     "type": "object",
#                     "properties": {
#                         "request_id": {"type": "string", "description": "请求唯一标识"},
#                         "timestamp": {"type": "string", "description": "操作时间戳"},
#                         "execution_time": {"type": "number", "description": "执行耗时（毫秒）"},
#                         "function_name": {"type": "string", "description": "执行的函数名"},
#                         "node_version": {"type": "string", "description": "节点版本"},
#                         "author": {"type": "string", "description": "节点作者"}
#                     },
#                     "description": "操作元数据信息"
#                 },
#
#                 # 额外信息
#                 "info": {
#                     "type": "object",
#                     "description": "附加信息和上下文"
#                 }
#             },
#             "required": ["status", "success", "metadata"]
#         }
#
#         return MCPService(
#             name="camera_service",
#             version="2.1.0",
#             description="专业相机服务，支持拍照、录像、参数调节等完整功能，统一返回结构",
#
#             # 全局参数
#             global_parameters=[
#                 MCPParameter(
#                     name="output_dir",
#                     type="string",
#                     description="输出目录路径",
#                     required=True,
#                     default="./output"
#                 )
#             ],
#
#             # 功能函数 - 优化描述
#             functions=[
#                 MCPFunction(
#                     name="take_photo",
#                     description="拍摄单张照片。支持自定义文件名和图像质量调节，以及临时的相机参数覆盖（如亮度、对比度等）。如不指定参数，系统将使用智能默认值。",
#                     parameters=[
#                         MCPParameter(
#                             "filename",
#                             "string",
#                             "照片保存文件名（不含扩展名）。如不填写，系统会自动生成基于时间戳的文件名，格式为 'photo_相机ID_时间戳'。",
#                             False
#                         ),
#                         MCPParameter(
#                             "quality",
#                             "int",
#                             "JPEG 图像质量等级 (1-100)，数值越高质量越好但文件越大。默认 95 为高质量设置。",
#                             False,
#                             95,
#                             {"min": 1, "max": 100}
#                         ),
#                         MCPParameter(
#                             "temp_brightness",
#                             "float",
#                             "临时亮度调节 (0.0-1.0)，仅对本次拍照生效。0.0=最暗，1.0=最亮。留空则使用当前相机设置。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "temp_contrast",
#                             "float",
#                             "临时对比度调节 (0.0-1.0)，仅对本次拍照生效。0.0=无对比度，1.0=最高对比度。留空则使用当前设置。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "temp_saturation",
#                             "float",
#                             "临时饱和度调节 (0.0-1.0)，仅对本次拍照生效。0.0=灰度图像，1.0=色彩最鲜艳。留空则使用当前设置。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "temp_exposure",
#                             "float",
#                             "临时曝光补偿 (-10.0 到 5.0)，仅对本次拍照生效。负值=较暗，正值=较亮。留空则使用当前设置。",
#                             False,
#                             constraints={"min": -10.0, "max": 5.0}
#                         )
#                     ],
#                     return_schema=unified_return_schema
#                 ),
#
#                 MCPFunction(
#                     name="record_video",
#                     description="录制视频。支持自定义时长、文件名和编码格式，可启用实时进度监控。支持临时参数覆盖以调节录制质量。系统会自动选择最佳编码器。",
#                     parameters=[
#                         MCPParameter(
#                             "duration",
#                             "int",
#                             "录制时长（秒）。必填参数，范围 1-3600 秒（1小时）。建议短视频使用 10-60 秒。",
#                             True,
#                             constraints={"min": 1, "max": 3600}
#                         ),
#                         MCPParameter(
#                             "filename",
#                             "string",
#                             "视频保存文件名（不含扩展名）。如不填写，系统会自动生成格式为 'video_相机ID_时间戳' 的文件名。",
#                             False
#                         ),
#                         MCPParameter(
#                             "codec_preference",
#                             "string",
#                             "首选视频编码格式。H264=最佳兼容性，XVID=较小文件，MJPG=最快处理，auto=系统自动选择。默认 H264。",
#                             False,
#                             "H264",
#                             {"enum": ["H264", "XVID", "MJPG", "auto"]}
#                         ),
#                         MCPParameter(
#                             "enable_progress",
#                             "bool",
#                             "是否启用录制进度实时输出。启用后会在返回结果中包含详细的进度日志信息。默认关闭以提高性能。",
#                             False,
#                             False
#                         ),
#                         MCPParameter(
#                             "temp_fps",
#                             "float",
#                             "临时帧率设置 (1.0-120.0 fps)，仅对本次录制生效。较高帧率=更流畅但文件更大。留空则使用系统默认。",
#                             False,
#                             constraints={"min": 1.0, "max": 120.0}
#                         ),
#                         MCPParameter(
#                             "temp_brightness",
#                             "float",
#                             "临时亮度调节 (0.0-1.0)，仅对本次录制生效。影响整个视频的亮度表现。留空则使用当前设置。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "temp_contrast",
#                             "float",
#                             "临时对比度调节 (0.0-1.0)，仅对本次录制生效。影响视频的对比度和清晰度。留空则使用当前设置。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         )
#                     ],
#                     return_schema=unified_return_schema
#                 ),
#
#                 MCPFunction(
#                     name="update_camera_parameters",
#                     description="更新相机的全局参数设置。这些设置会影响后续所有拍照和录像操作，直到再次修改。系统会自动验证参数有效性并进行实时测试。",
#                     parameters=[
#                         MCPParameter(
#                             "brightness",
#                             "float",
#                             "全局亮度设置 (0.0-1.0)。0.0=最暗，0.5=中等亮度，1.0=最亮。调节后影响所有后续拍摄。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "contrast",
#                             "float",
#                             "全局对比度设置 (0.0-1.0)。0.0=无对比度（平坦），0.5=标准对比度，1.0=最高对比度（锐利）。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "saturation",
#                             "float",
#                             "全局色彩饱和度 (0.0-1.0)。0.0=灰度图像，0.5=自然色彩，1.0=色彩最鲜艳。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "hue",
#                             "float",
#                             "全局色调偏移 (0.0-1.0)。调节整体色彩倾向，0.0和1.0为自然色调，0.5为色调反转。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "gain",
#                             "float",
#                             "全局增益/ISO 敏感度 (0.0-10.0)。类似相机 ISO 设置，数值越高在暗光下表现越好但噪点越多。",
#                             False,
#                             constraints={"min": 0.0, "max": 10.0}
#                         ),
#                         MCPParameter(
#                             "exposure",
#                             "float",
#                             "全局曝光补偿 (-10.0 到 5.0)。负值使图像变暗，正值使图像变亮。0为自动曝光。",
#                             False,
#                             constraints={"min": -10.0, "max": 5.0}
#                         ),
#                         MCPParameter(
#                             "fps",
#                             "float",
#                             "全局帧率设置 (1.0-120.0 fps)。影响视频录制的流畅度，常用值：24/30/60 fps。",
#                             False,
#                             constraints={"min": 1.0, "max": 120.0}
#                         ),
#                         MCPParameter(
#                             "width",
#                             "int",
#                             "全局画面宽度像素 (320-4096)。与高度共同决定分辨率。常用：640、1280、1920。",
#                             False,
#                             constraints={"min": 320, "max": 4096}
#                         ),
#                         MCPParameter(
#                             "height",
#                             "int",
#                             "全局画面高度像素 (240-4096)。与宽度共同决定分辨率。常用：480、720、1080。",
#                             False,
#                             constraints={"min": 240, "max": 4096}
#                         ),
#                         MCPParameter(
#                             "auto_focus",
#                             "bool",
#                             "是否启用自动对焦。true=相机自动调节焦点，false=使用手动对焦值。大多数情况建议启用。",
#                             False
#                         ),
#                         MCPParameter(
#                             "focus",
#                             "float",
#                             "手动对焦值 (0.0-1.0)。仅在关闭自动对焦时生效。0.0=近焦，1.0=远焦，0.5=中等距离。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         )
#                     ],
#                     return_schema=unified_return_schema
#                 ),
#
#                 MCPFunction(
#                     name="get_camera_info",
#                     description="获取相机的完整状态信息和配置详情。包括当前参数设置、分辨率、帧率、可用性状态等。用于诊断相机状态和确认设置。",
#                     parameters=[],
#                     return_schema=unified_return_schema
#                 ),
#
#                 MCPFunction(
#                     name="test_camera",
#                     description="执行相机功能测试。检测相机是否可访问、能否正常捕获画面、获取基本性能参数。建议在开始使用前或遇到问题时运行此测试。",
#                     parameters=[],
#                     return_schema=unified_return_schema
#                 ),
#
#                 MCPFunction(
#                     name="batch_photos",
#                     description="批量连续拍摄多张照片。支持自定义拍摄间隔、文件名模式和统一的图像参数。适用于延时摄影、连拍或文档批量拍摄场景。",
#                     parameters=[
#                         MCPParameter(
#                             "count",
#                             "int",
#                             "拍摄照片数量 (1-100 张)。必填参数。建议根据存储空间和用途合理设置，大批量拍摄请注意磁盘空间。",
#                             True,
#                             constraints={"min": 1, "max": 100}
#                         ),
#                         MCPParameter(
#                             "interval",
#                             "float",
#                             "拍摄间隔时间（秒，0.0-60.0）。两张照片之间的等待时间。0.0=连续快拍，1.0-5.0=常规间隔，10.0+=延时摄影。",
#                             False,
#                             1.0,
#                             {"min": 0.0, "max": 60.0}
#                         ),
#                         MCPParameter(
#                             "quality",
#                             "int",
#                             "统一的 JPEG 质量等级 (1-100)。应用于所有照片。推荐：60-80=平衡质量，85-95=高质量，95+=最高质量。",
#                             False,
#                             95,
#                             {"min": 1, "max": 100}
#                         ),
#                         MCPParameter(
#                             "filename_pattern",
#                             "string",
#                             "文件名命名模式。支持占位符 {index}=序号，{timestamp}=时间戳。例如：'batch_{index}' 生成 batch_1, batch_2...",
#                             False,
#                             "batch_{index}"
#                         ),
#                         MCPParameter(
#                             "enable_progress",
#                             "bool",
#                             "是否启用拍摄进度实时输出。启用后可监控批量拍摄进度，但会略微影响性能。默认关闭。",
#                             False,
#                             False
#                         ),
#                         MCPParameter(
#                             "temp_brightness",
#                             "float",
#                             "批量拍摄统一亮度 (0.0-1.0)。应用于所有照片的临时亮度设置。留空则使用当前全局设置。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         ),
#                         MCPParameter(
#                             "temp_contrast",
#                             "float",
#                             "批量拍摄统一对比度 (0.0-1.0)。应用于所有照片的临时对比度设置。留空则使用当前全局设置。",
#                             False,
#                             constraints={"min": 0.0, "max": 1.0}
#                         )
#                     ],
#                     return_schema=unified_return_schema
#                 ),
#
#                 MCPFunction(
#                     name="reset_to_camera_defaults",
#                     description="重置所有相机参数为系统自动检测的最佳默认值。清除所有手动设置，让相机恢复到最适合当前硬件的智能配置状态。",
#                     parameters=[],
#                     return_schema=unified_return_schema
#                 )
#             ],
#
#             metadata={
#                 "author": "Gordon",
#                 "category": "camera",
#                 "tags": ["camera", "photo", "video", "capture", "opencv", "auto-detection", "unified-response"],
#                 "created_at": "2025-08-21T11:18:47Z",
#                 "updated_at": "2025-08-21T11:18:47Z",
#                 "dependencies": [
#                     "opencv-python>=4.5.0",
#                     "numpy>=1.21.0",
#                     "pathlib",
#                     "logging"
#                 ],
#                 "features": [
#                     "智能参数自动检测",
#                     "临时参数覆盖",
#                     "实时相机测试",
#                     "进度回调支持",
#                     "批量操作",
#                     "多种视频编码",
#                     "完整错误处理",
#                     "统一返回结构"
#                 ]
#             }
#         )
#
#     def __init__(self, **global_params):
#         """初始化 MCP 节点，创建 CameraService 实例"""
#         super().__init__(**global_params)
#
#         # 创建相机参数模型
#         self.camera_model = self._create_camera_model()
#
#         # 创建相机服务实例
#         self.camera_service = CameraService(self.camera_model)
#
#         # 节点信息
#         self.node_version = "1.0"
#         self.author = "Gordon"
#
#         logger_handler.info(f"CameraMCPNode initialized - Camera ID: {self.camera_model.camera_id}, "
#                     f"Output: {self.camera_model.output_dir}, Author: {self.author}")
#
#     def _create_camera_model(self) -> CameraParameterBase:
#         """从全局参数创建相机模型"""
#         valid_params = {k: v for k, v in self.global_params.items() if v is not None}
#
#         if 'fps' in valid_params:
#             return VideoParameters(**valid_params)
#         else:
#             return CameraParameterBase(**valid_params)
#
#     def _create_unified_response(self,
#                                  function_name: str,
#                                  status: str = "success",
#                                  data: Optional[Dict[str, Any]] = None,
#                                  error: Optional[Dict[str, Any]] = None,
#                                  info: Optional[Dict[str, Any]] = None,
#                                  start_time: Optional[float] = None) -> Dict[str, Any]:
#         """创建统一格式的响应"""
#
#         # 计算执行时间
#         execution_time = (time.time() - start_time) * 1000 if start_time else 0
#
#         response = {
#             "status": status,
#             "success": status == "success",
#             "metadata": {
#                 "request_id": str(uuid.uuid4()),
#                 "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "Z",
#                 "execution_time": round(execution_time, 2),
#                 "function_name": function_name,
#                 "node_version": self.node_version,
#                 "author": self.author
#             }
#         }
#
#         if data:
#             response["data"] = data
#
#         if error:
#             response["error"] = error
#
#         if info:
#             response["info"] = info
#
#         return response
#
#     def execute_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
#         """执行指定函数 - 统一返回格式"""
#         start_time = time.time()
#
#         try:
#             if function_name == "take_photo":
#                 return self._take_photo(start_time, **kwargs)
#             elif function_name == "record_video":
#                 return self._record_video(start_time, **kwargs)
#             elif function_name == "update_camera_parameters":
#                 return self._update_camera_parameters(start_time, **kwargs)
#             elif function_name == "get_camera_info":
#                 return self._get_camera_info(start_time, **kwargs)
#             elif function_name == "test_camera":
#                 return self._test_camera(start_time, **kwargs)
#             elif function_name == "batch_photos":
#                 return self._batch_photos(start_time, **kwargs)
#             elif function_name == "reset_to_camera_defaults":
#                 return self._reset_to_camera_defaults(start_time, **kwargs)
#             else:
#                 available_functions = [f.name for f in self.get_service_definition().functions]
#                 return self._create_unified_response(
#                     function_name=function_name,
#                     status="error",
#                     error={
#                         "code": "UNKNOWN_FUNCTION",
#                         "message": f"未知函数: {function_name}",
#                         "details": {"available_functions": available_functions}
#                     },
#                     start_time=start_time
#                 )
#
#         except Exception as e:
#             logger_handler.error(f"执行函数 {function_name} 失败: {e}")
#             return self._create_unified_response(
#                 function_name=function_name,
#                 status="error",
#                 error={
#                     "code": "EXECUTION_ERROR",
#                     "message": f"函数执行异常: {str(e)}",
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 start_time=start_time
#             )
#
#     def _take_photo(self, start_time: float, filename: Optional[str] = None,
#                     quality: int = 95, **kwargs) -> Dict[str, Any]:
#         """拍照实现 - 统一返回格式"""
#         try:
#             # 创建临时参数覆盖
#             temp_params = self._extract_temp_params(kwargs, PhotoParameters)
#
#             # 调用真实的相机服务
#             service_result = self.camera_service.take_photo(
#                 filename=filename,
#                 quality=quality,
#                 photo_params=temp_params
#             )
#
#             if service_result.get("status") == "success":
#                 # 提取核心数据
#                 data = {
#                     "file_path": service_result.get("file_path"),
#                     "filename": service_result.get("filename"),
#                     "file_size": service_result.get("file_size"),
#                     "resolution": service_result.get("resolution"),
#                     "quality": service_result.get("quality")
#                 }
#
#                 # 附加信息
#                 info = {
#                     "camera_params": service_result.get("camera_params", {}),
#                     "temp_params_used": temp_params.to_dict() if temp_params else None,
#                     "capture_type": "single_photo"
#                 }
#
#                 logger_handler.info(f"Photo taken: {data.get('filename', 'unknown')}")
#
#                 return self._create_unified_response(
#                     function_name="take_photo",
#                     status="success",
#                     data=data,
#                     info=info,
#                     start_time=start_time
#                 )
#             else:
#                 return self._create_unified_response(
#                     function_name="take_photo",
#                     status="error",
#                     error={
#                         "code": "PHOTO_CAPTURE_FAILED",
#                         "message": service_result.get("message", "拍照失败"),
#                         "details": service_result
#                     },
#                     start_time=start_time
#                 )
#
#         except Exception as e:
#             logger_handler.error(f"拍照失败: {e}")
#             return self._create_unified_response(
#                 function_name="take_photo",
#                 status="error",
#                 error={
#                     "code": "PHOTO_EXCEPTION",
#                     "message": str(e),
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 start_time=start_time
#             )
#
#     def _record_video(self, start_time: float, duration: int, filename: Optional[str] = None,
#                       codec_preference: Optional[str] = None, enable_progress: bool = False,
#                       **kwargs) -> Dict[str, Any]:
#         """录像实现 - 统一返回格式"""
#         try:
#             # 创建临时参数覆盖
#             temp_params = self._extract_temp_params(kwargs, VideoParameters)
#
#             # 设置进度回调
#             progress_callback = None
#             progress_log = []
#
#             if enable_progress:
#                 def progress_cb(progress: float, info: Dict[str, Any]):
#                     log_entry = {
#                         "timestamp": time.strftime("%H:%M:%S"),
#                         "progress": f"{progress:.1%}",
#                         "info": info
#                     }
#                     progress_log.append(log_entry)
#                     logger_handler.debug(f"录像进度: {progress:.1%}")
#
#                 progress_callback = progress_cb
#
#             # 调用真实的相机服务
#             service_result = self.camera_service.record_video(
#                 duration=duration,
#                 filename=filename,
#                 video_params=temp_params,
#                 progress_callback=progress_callback,
#                 codec_preference=codec_preference
#             )
#
#             if service_result.get("status") == "success":
#                 # 提取核心数据
#                 data = {
#                     "file_path": service_result.get("file_path"),
#                     "filename": service_result.get("filename"),
#                     "file_size": service_result.get("file_size"),
#                     "duration": service_result.get("duration"),
#                     "planned_duration": service_result.get("planned_duration"),
#                     "frames_written": service_result.get("frames_written"),
#                     "total_frames": service_result.get("total_frames"),
#                     "fps": service_result.get("fps"),
#                     "resolution": service_result.get("resolution")
#                 }
#
#                 # 附加信息
#                 info = {
#                     "camera_params": service_result.get("camera_params", {}),
#                     "temp_params_used": temp_params.to_dict() if temp_params else None,
#                     "frame_efficiency": service_result.get("frame_efficiency"),
#                     "codec_used": codec_preference or "auto",
#                     "progress_log": progress_log if enable_progress else None,
#                     "capture_type": "video_recording"
#                 }
#
#                 logger_handler.info(f"Video recorded: {data.get('filename', 'unknown')} - Duration: {data.get('duration', 0)}s")
#
#                 return self._create_unified_response(
#                     function_name="record_video",
#                     status="success",
#                     data=data,
#                     info=info,
#                     start_time=start_time
#                 )
#             else:
#                 return self._create_unified_response(
#                     function_name="record_video",
#                     status="error",
#                     error={
#                         "code": "VIDEO_RECORDING_FAILED",
#                         "message": service_result.get("message", "录像失败"),
#                         "details": service_result
#                     },
#                     start_time=start_time
#                 )
#
#         except Exception as e:
#             logger_handler.error(f"录像失败: {e}")
#             return self._create_unified_response(
#                 function_name="record_video",
#                 status="error",
#                 error={
#                     "code": "VIDEO_EXCEPTION",
#                     "message": str(e),
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 start_time=start_time
#             )
#
#     def _update_camera_parameters(self, start_time: float, **kwargs) -> Dict[str, Any]:
#         """更新相机参数 - 统一返回格式"""
#         try:
#             # 过滤出有效的参数更新
#             update_params = {k: v for k, v in kwargs.items() if v is not None}
#
#             if not update_params:
#                 return self._create_unified_response(
#                     function_name="update_camera_parameters",
#                     status="error",
#                     error={
#                         "code": "NO_PARAMETERS",
#                         "message": "没有提供要更新的参数",
#                         "details": {"available_params": list(kwargs.keys())}
#                     },
#                     start_time=start_time
#                 )
#
#             # 调用相机服务更新参数
#             service_result = self.camera_service.update_camera_parameters(**update_params)
#
#             changes = service_result.get("changes", {})
#             errors = service_result.get("errors", {})
#
#             # 确定状态
#             if changes and not errors:
#                 status = "success"
#             elif changes and errors:
#                 status = "warning"
#             else:
#                 status = "error" if errors else "warning"
#
#             # 提取核心数据
#             data = {
#                 "changes": changes,
#                 "validation_errors": errors,
#                 "camera_test_result": service_result.get("camera_test"),
#                 "actual_values": service_result.get("actual_values")
#             }
#
#             # 附加信息
#             info = {
#                 "update_summary": {
#                     "total_params": len(update_params),
#                     "changed_params": len(changes),
#                     "failed_params": len(errors),
#                     "test_passed": "camera_test" in service_result and not service_result.get("camera_test_error")
#                 },
#                 "requested_params": update_params,
#                 "operation_type": "parameter_update"
#             }
#
#             logger_handler.info(f"参数更新完成: {len(changes)} 个参数变更")
#
#             return self._create_unified_response(
#                 function_name="update_camera_parameters",
#                 status=status,
#                 data=data,
#                 info=info,
#                 start_time=start_time
#             )
#
#         except Exception as e:
#             logger_handler.error(f"参数更新失败: {e}")
#             return self._create_unified_response(
#                 function_name="update_camera_parameters",
#                 status="error",
#                 error={
#                     "code": "PARAMETER_UPDATE_EXCEPTION",
#                     "message": str(e),
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 start_time=start_time
#             )
#
#     def _get_camera_info(self, start_time: float) -> Dict[str, Any]:
#         """获取相机信息 - 统一返回格式"""
#         try:
#             service_result = self.camera_service.get_camera_info()
#
#             if service_result.get("status") == "success":
#                 # 提取核心数据
#                 data = {
#                     "camera_id": service_result.get("camera_id"),
#                     "resolution": service_result.get("resolution"),
#                     "fps": service_result.get("fps"),
#                     "available": service_result.get("available", True),
#                     "current_settings": service_result.get("current_settings"),
#                     "model_config": service_result.get("model_config")
#                 }
#
#                 # 附加信息
#                 info = {
#                     "capture_test": service_result.get("capture_test"),
#                     "output_dir": service_result.get("output_dir"),
#                     "operation_type": "camera_info_query"
#                 }
#
#                 logger_handler.debug(f"获取相机信息: Camera {data.get('camera_id', 'unknown')}")
#
#                 return self._create_unified_response(
#                     function_name="get_camera_info",
#                     status="success",
#                     data=data,
#                     info=info,
#                     start_time=start_time
#                 )
#             else:
#                 return self._create_unified_response(
#                     function_name="get_camera_info",
#                     status="error",
#                     error={
#                         "code": "CAMERA_INFO_FAILED",
#                         "message": service_result.get("message", "获取相机信息失败"),
#                         "details": service_result
#                     },
#                     start_time=start_time
#                 )
#
#         except Exception as e:
#             logger_handler.error(f"获取相机信息失败: {e}")
#             return self._create_unified_response(
#                 function_name="get_camera_info",
#                 status="error",
#                 error={
#                     "code": "CAMERA_INFO_EXCEPTION",
#                     "message": str(e),
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 start_time=start_time
#             )
#
#     def _test_camera(self, start_time: float) -> Dict[str, Any]:
#         """测试相机 - 统一返回格式"""
#         try:
#             service_result = self.camera_service.test_camera()
#
#             if service_result.get("status") == "success":
#                 # 提取核心数据
#                 data = {
#                     "available": service_result.get("available"),
#                     "can_capture": service_result.get("can_capture"),
#                     "test_results": {
#                         "resolution": service_result.get("resolution"),
#                         "channels": service_result.get("channels"),
#                         "dtype": service_result.get("dtype"),
#                         "frame_size": service_result.get("frame_size")
#                     }
#                 }
#
#                 # 附加信息
#                 info = {
#                     "test_type": "basic_functionality",
#                     "camera_id": self.camera_model.camera_id,
#                     "operation_type": "camera_test"
#                 }
#
#                 logger_handler.info(f"相机测试完成: Available={data['available']}, Can Capture={data['can_capture']}")
#
#                 return self._create_unified_response(
#                     function_name="test_camera",
#                     status="success",
#                     data=data,
#                     info=info,
#                     start_time=start_time
#                 )
#             else:
#                 return self._create_unified_response(
#                     function_name="test_camera",
#                     status="error",
#                     error={
#                         "code": "CAMERA_TEST_FAILED",
#                         "message": service_result.get("error", "相机测试失败"),
#                         "details": service_result
#                     },
#                     data={
#                         "available": service_result.get("available", False),
#                         "can_capture": service_result.get("can_capture", False)
#                     },
#                     start_time=start_time
#                 )
#
#         except Exception as e:
#             logger_handler.error(f"相机测试失败: {e}")
#             return self._create_unified_response(
#                 function_name="test_camera",
#                 status="error",
#                 error={
#                     "code": "CAMERA_TEST_EXCEPTION",
#                     "message": str(e),
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 data={
#                     "available": False,
#                     "can_capture": False
#                 },
#                 start_time=start_time
#             )
#
#     def _batch_photos(self, start_time: float, count: int, interval: float = 1.0,
#                       quality: int = 95, filename_pattern: str = "batch_{index}",
#                       enable_progress: bool = False, **kwargs) -> Dict[str, Any]:
#         """批量拍照 - 统一返回格式"""
#         try:
#             # 创建临时参数覆盖
#             temp_params = self._extract_temp_params(kwargs, PhotoParameters)
#
#             # 设置进度回调
#             progress_callback = None
#             progress_log = []
#
#             if enable_progress:
#                 def progress_cb(current: int, total: int):
#                     log_entry = {
#                         "timestamp": time.strftime("%H:%M:%S"),
#                         "progress": f"{current}/{total} ({current / total:.1%})",
#                         "current": current,
#                         "total": total
#                     }
#                     progress_log.append(log_entry)
#                     logger_handler.debug(f"批量拍照进度: {current}/{total}")
#
#                 progress_callback = progress_cb
#
#             # 调用相机服务
#             service_result = self.camera_service.batch_photos(
#                 count=count,
#                 interval=interval,
#                 photo_params=temp_params,
#                 progress_callback=progress_callback
#             )
#
#             if service_result.get("status") == "success":
#                 # 提取核心数据
#                 data = {
#                     "total_requested": service_result.get("total_requested"),
#                     "successful_captures": service_result.get("successful_captures"),
#                     "failed_captures": service_result.get("failed_captures"),
#                     "results": service_result.get("results", [])
#                 }
#
#                 # 计算总文件大小
#                 total_file_size = sum(
#                     result.get("file_size", 0)
#                     for result in data["results"]
#                     if result.get("status") == "success"
#                 )
#
#                 # 附加信息
#                 info = {
#                     "camera_params": service_result.get("camera_params", {}),
#                     "batch_summary": {
#                         "success_rate": f"{data['successful_captures'] / data['total_requested'] * 100:.1f}%",
#                         "total_time_estimate": count * interval,
#                         "average_interval": interval,
#                         "quality_used": quality,
#                         "total_file_size": total_file_size,
#                         "filename_pattern": filename_pattern
#                     },
#                     "temp_params_used": temp_params.to_dict() if temp_params else None,
#                     "progress_log": progress_log if enable_progress else None,
#                     "operation_type": "batch_photos"
#                 }
#
#                 logger_handler.info(f"批量拍照完成: {data['successful_captures']}/{count} 成功")
#
#                 return self._create_unified_response(
#                     function_name="batch_photos",
#                     status="success",
#                     data=data,
#                     info=info,
#                     start_time=start_time
#                 )
#             else:
#                 return self._create_unified_response(
#                     function_name="batch_photos",
#                     status="error",
#                     error={
#                         "code": "BATCH_PHOTOS_FAILED",
#                         "message": service_result.get("message", "批量拍照失败"),
#                         "details": service_result
#                     },
#                     start_time=start_time
#                 )
#
#         except Exception as e:
#             logger_handler.error(f"批量拍照失败: {e}")
#             return self._create_unified_response(
#                 function_name="batch_photos",
#                 status="error",
#                 error={
#                     "code": "BATCH_PHOTOS_EXCEPTION",
#                     "message": str(e),
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 start_time=start_time
#             )
#
#     def _reset_to_camera_defaults(self, start_time: float) -> Dict[str, Any]:
#         """重置相机默认值 - 统一返回格式"""
#         try:
#             service_result = self.camera_service.reset_to_camera_defaults()
#
#             if service_result.get("status") == "success":
#                 # 提取核心数据
#                 data = {
#                     "changes": service_result.get("changes", {}),
#                     "auto_detected_defaults": service_result.get("auto_detected_defaults", {}),
#                     "detection_timestamp": service_result.get("detection_timestamp")
#                 }
#
#                 # 附加信息
#                 info = {
#                     "reset_summary": {
#                         "parameters_reset": len(data["changes"]),
#                         "detection_method": "camera_auto_detection",
#                         "service_user": service_result.get("service_user", "system")
#                     },
#                     "operation_type": "parameter_reset"
#                 }
#
#                 logger_handler.info(f"相机参数重置完成: {len(data['changes'])} 个参数被重置")
#
#                 return self._create_unified_response(
#                     function_name="reset_to_camera_defaults",
#                     status="success",
#                     data=data,
#                     info=info,
#                     start_time=start_time
#                 )
#             else:
#                 return self._create_unified_response(
#                     function_name="reset_to_camera_defaults",
#                     status="error",
#                     error={
#                         "code": "RESET_DEFAULTS_FAILED",
#                         "message": service_result.get("message", "重置默认值失败"),
#                         "details": service_result
#                     },
#                     start_time=start_time
#                 )
#
#         except Exception as e:
#             logger_handler.error(f"重置相机默认值失败: {e}")
#             return self._create_unified_response(
#                 function_name="reset_to_camera_defaults",
#                 status="error",
#                 error={
#                     "code": "RESET_DEFAULTS_EXCEPTION",
#                     "message": str(e),
#                     "details": {"exception_type": type(e).__name__}
#                 },
#                 start_time=start_time
#             )
#
#     def _extract_temp_params(self, kwargs: Dict[str, Any], param_class: type) -> Optional[object]:
#         """从 kwargs 中提取临时参数并创建参数对象"""
#         temp_params = {}
#
#         # 提取所有以 temp_ 开头的参数
#         for key, value in kwargs.items():
#             if key.startswith("temp_") and value is not None:
#                 param_name = key[5:]  # 移除 temp_ 前缀
#                 temp_params[param_name] = value
#
#         # 如果有临时参数，创建参数对象
#         if temp_params:
#             # 继承当前相机模型的基础参数
#             base_params = self.camera_model.to_dict()
#             merged_params = {**base_params, **temp_params}
#
#             try:
#                 return param_class.from_dict(merged_params)
#             except Exception as e:
#                 logger_handler.warning(f"创建临时参数对象失败: {e}")
#                 return None
#
#         return None
#
#
#
# if __name__ == '__main__':
#     node = CameraMCPNode.get_service_definition()
#     print(node)