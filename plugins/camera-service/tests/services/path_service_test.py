from utils.file_path_manager import PathService


def example_usage():
    # 初始化路径服务
    path_service = PathService()

    # 生成视频路径
    video_path1 = path_service.generate_video_path()
    print(f"Auto video path: {video_path1}")
    # 输出: output/2025/08/20/073716_123_video.mp4

    video_path2 = path_service.generate_video_path("my_recording")
    print(f"Custom video path: {video_path2}")
    # 输出: output/2025/08/20/my_recording.mp4

    # 生成照片路径
    photo_path1 = path_service.generate_photo_path()
    print(f"Auto photo path: {photo_path1}")
    # 输出: output/2025/08/20/073716_456_photo.jpg

    photo_path2 = path_service.generate_photo_path("portrait")
    print(f"Custom photo path: {photo_path2}")
    # 输出: output/2025/08/20/portrait.jpg

    # 获取今天的文件夹
    today_folder = path_service.get_today_folder()
    print(f"Today's folder: {today_folder}")
    # 输出: output/2025/08/20

    # 清理旧文件
    deleted = path_service.cleanup_old_files(days_to_keep=7)
    print(f"Deleted {deleted} old files")


if __name__ == "__main__":
    example_usage()
