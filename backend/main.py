"""
智能校园失物招领系统 - 后端入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import traceback

from app.api.v1 import auth, items, favorites, common, messages, ai, search, recommend
from app.config import settings
from app.services.scheduler_service import start_scheduler, stop_scheduler

app = FastAPI(
    title="Smart Campus L&F API",
    description="智能校园失物招领系统 API",
    version="1.0.0"
)

# CORS - 微信小程序需配置合法域名，开发时可允许本地
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - Base URL: /api/v1
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(items.router, prefix="/api/v1/items", tags=["物品"])
app.include_router(favorites.router, prefix="/api/v1/favorites", tags=["收藏"])
app.include_router(common.router, prefix="/api/v1/common", tags=["公共"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["消息"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(search.router, prefix="/api/v1/search", tags=["搜索"])
app.include_router(recommend.router, prefix="/api/v1/recommend", tags=["推荐"])

# 静态文件（上传的图片）
import os
upload_dir = settings.upload_dir
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

@app.get("/")
def root():
    return {
        "message": "Smart Campus L&F API",
        "docs": "/docs",
        "recommend_paths": [
            "/api/v1/items/{item_id}/recommendations?limit=10",
            "/api/v1/recommend/related?item_id=1&limit=10",
        ],
    }


@app.on_event("startup")
async def on_startup():
    start_scheduler()


@app.on_event("shutdown")
async def on_shutdown():
    stop_scheduler()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"code": 50000, "message": str(exc), "data": None})
