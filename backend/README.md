# 智能校园失物招领 - 后端 API

基于 **Python FastAPI**，便于对接 YOLO、OCR、CLIP 等 AI 模型。

## 环境要求

- Python 3.10+
- MySQL 8.0+

## 快速开始

### 1. 创建数据库

```bash
python scripts/init_db.py
python scripts/seed_data.py
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
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

访问 http://localhost:8080/docs 查看 API 文档。

## 项目结构

```
backend/
├── main.py              # 入口
├── requirements.txt
├── app/
│   ├── config.py         # 配置
│   ├── database.py       # 数据库
│   ├── core/             # 安全、依赖、统一响应
│   ├── schemas/          # DTO
│   ├── repositories/     # 数据访问层
│   ├── services/         # 业务服务层
│   ├── models/           # ORM 模型
│   └── api/v1/           # 控制层路由
└── uploads/             # 上传文件目录
```

## 后续开发

- **YOLO/OCR/CLIP**：在 `app/services` 新增 `ai_service` 并在发布流程中异步调用
- **JWT 鉴权**：当前基础版已接入，可按角色扩展权限
- **OSS 存储**：将 `api/v1/common.py` 上传逻辑替换为 OSS

## YOLO 手动识别接口

- `POST /api/v1/ai/recognize/item/{item_id}`：手动触发识别
- `POST /api/v1/ai/apply-suggestion`：发布者采用识别建议
- `GET /api/v1/ai/health`：AI健康检查

云推理可选：见 `inference_service/README.md`。
