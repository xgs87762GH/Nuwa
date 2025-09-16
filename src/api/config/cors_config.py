from src.core.config import get_app_config

application = get_app_config()


def get_cors_origins():
    """根据环境返回允许的源"""
    if ["development", "dev", "staging"] == application.environment:
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ]
    elif ["production", "prod"] == application.environment:
        return [
            "https://yourdomain.com",
            "https://www.yourdomain.com",
            # 添加你的生产域名
        ]
    else:
        return ["*"]  # 测试环境允许所有源


def get_cors_config():
    """获取CORS配置"""
    return {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
        ],
    }
