from pydantic import BaseModel, Field
from pydantic import field_validator


class AppConfig(BaseModel):
    name: str = Field(description="Application name")
    version: str = Field("1.0.0", description="Application version")
    description: str = Field(description="Application description")
    debug: bool = Field(description="Enable debug mode")
    host: str = Field("0.0.0.0", description="Server host address")
    port: int = Field(8000, ge=1, le=65535, description="Server port number")
    environment: str = Field(description="Application environment")
    readme: str = Field(description="README file path")
    authors: list[dict] = Field(description="List of authors")
    license: dict = Field(description="License information")
    requires_python: str = Field(description="Required Python version")
    keywords: list[str] = Field(description="Application keywords")

    @field_validator('host')
    @classmethod
    def validate_host(cls, v):
        import re
        # Check if it's a valid IP address pattern or common hostnames
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if v in ['0.0.0.0', 'localhost', '127.0.0.1'] or re.match(ip_pattern, v):
            return v
        raise ValueError('Host must be a valid IP address or hostname')

    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ['development', 'testing', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f'Environment must be one of: {", ".join(valid_envs)}')
        return v.lower()

    @field_validator('requires_python')
    @classmethod
    def validate_python_version(cls, v):
        import re
        pattern = r'^>=\d+\.\d+(\.\d+)?$'
        if not re.match(pattern, v):
            raise ValueError('Python version must be in format ">=X.Y" or ">=X.Y.Z"')
        return v
