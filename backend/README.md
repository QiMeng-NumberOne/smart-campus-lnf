# 智能校园失物招领 - 后端 API

基于 **Python FastAPI**，便于对接 YOLO、OCR、CLIP 等 AI 模型。

## 环境要求

- Python 3.10+
- MySQL 8.0+

## 快速开始

### 1. 创建数据库

```bash
mysql -u root -p -e "CREATE DATABASE smart_campus_lnf CHARACTER SET utf8mb4;"
mysql -u root -p smart_campus_lnf < docs/03_database/schema.sql
```

### 2. 配置环境

```bash
cd backend
cp .env.example .env
# 编辑 .env 修改 DATABASE_URL 等
```

### 3. 安装依赖并启动

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

访问 http://localhost:8080/docs 查看 API 文档。

## 项目结构

```
backend/
├── main.py              # 入口
├── requirements.txt
├── app/
│   ├── config.py        # 配置
│   ├── database.py      # 数据库
│   ├── models/          # 数据模型
│   └── routers/         # 路由
│       ├── auth.py      # 认证
│       ├── items.py     # 物品 CRUD
│       ├── search.py    # 搜索
│       ├── ai.py        # AI 识别
│       ├── favorites.py # 收藏
│       └── common.py    # 公共接口
└── uploads/             # 上传文件目录
```

## 后续开发

- **YOLO/OCR/CLIP**：在 `app/routers/ai.py` 和 `app/routers/search.py` 中接入模型
- **JWT 鉴权**：实现 `get_current_user` 依赖并加在需登录的接口
- **OSS 存储**：修改 `common.upload` 上传至阿里云/腾讯云 OSS
