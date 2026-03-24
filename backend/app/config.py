"""
应用配置
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 服务
    base_url: str = "http://localhost:8080"  # 用于生成完整图片 URL
    # 数据库
    database_url: str = "mysql+pymysql://root:password@localhost:3306/smart_campus_lnf"
    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    # 上传
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()
