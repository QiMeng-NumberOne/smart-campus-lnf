# 微信云托管 / 通用容器部署：构建目录选 `backend/`，服务端口与控制台一致（默认 80）。
# 依赖含 PyTorch / Paddle / OpenCV，使用 Debian slim；勿用 alpine（与 PyTorch 轮子常不兼容）。
#
# 环境变量（在云托管「服务设置」中配置，勿把密钥提交进镜像）：
#   DATABASE_URL、JWT_SECRET、BASE_URL（须为公网 HTTPS 根地址，用于拼接上传图片 URL）
#   WECHAT_APPID、WECHAT_SECRET 等，参见 .env.example

FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# gcc/g++：供含 C 扩展的 Python 包编译；lib*：OpenCV / Paddle 等运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gcc g++ \
    libglib2.0-0 libgomp1 \
    libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖以利用层缓存
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p uploads

# 云托管默认映射容器 80；部分环境会注入 PORT
ENV PORT=80
EXPOSE 80

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-80}"]
