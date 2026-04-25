"""
应用配置
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 服务
    base_url: str = "http://127.0.0.1:8091"  # 用于生成完整图片 URL
    # 数据库
    database_url: str = "mysql+pymysql://root:123456@localhost:3306/lostfound_db?charset=utf8mb4"
    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    # 微信小程序登录
    wechat_appid: str = ""
    wechat_secret: str = ""
    wechat_subscribe_match_template_id: str = ""
    # 上传
    upload_dir: str = "./uploads"
    # AI
    ai_enabled: bool = True
    ai_model_path: str = "../yolo_model/runs/detect/yolo11_10_classes/weights/best.pt"
    ai_model_version: str = "campus_yolo_v1"
    ai_conf_threshold: float = 0.5
    ai_infer_url: str = ""
    ai_timeout_sec: float = 5.0
    # CLIP
    clip_model_name: str = "ViT-L-14-336"
    clip_device: str = "auto"  # auto/cpu/cuda
    clip_model_root: str = ""
    # 隐私加密
    sensitive_encrypt_key: str = ""
    # 定时任务
    scheduler_enabled: bool = True
    scheduler_timezone: str = "Asia/Shanghai"
    scheduler_weekly_day_of_week: str = "mon"
    scheduler_weekly_hour: int = 9
    scheduler_weekly_minute: int = 0
    scheduler_daily_match_hour: int = 9
    scheduler_daily_match_minute: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
