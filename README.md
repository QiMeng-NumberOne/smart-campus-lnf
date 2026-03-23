# smart-campus-lnf

智能校园失物招领系统（Smart Campus L&F）是一款专注于高校师生项目定制的现代化、数字化寻物与招领平台。传统的校园失物招领往往依赖线下交接或低效的群聊信息监听，信息容易被淹没且匹配率低下。本系统通过引入定制技术手段（如：基于 AI 的物品图像相似度匹配、LBS 丢失/拾取地点打卡、状态实现）无论是焦急寻找失物的失主，还是热心发布招领启事的同学，都通过本系统快速实现信息对接，用科技推动「物归原主」，打造更多温度的智慧校园。

## 项目结构

```
smart-campus-lnf/
├── docs/                # 项目文档（PRD、流程图、数据库、API）
├── frontend/            # 微信小程序前端
├── backend/             # Python FastAPI 后端
└── README.md
```

## 快速开始

### 后端

```bash
cd backend
# 1. 创建数据库并执行 docs/03_database/schema.sql
# 2. 配置 .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

### 前端

1. 用微信开发者工具打开 `frontend` 目录
2. 在 `project.config.json` 填入 AppID
3. 修改 `app.js` 中 `baseUrl` 为后端地址
4. 开发时勾选「不校验合法域名」
