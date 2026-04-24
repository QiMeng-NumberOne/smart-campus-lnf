# 智能校园失物招领系统（Smart Campus Lost & Found）

本项目是一个面向高校场景的失物招领平台，提供“寻物启事”和“失物招领”双链路闭环，并集成了 AI 能力（YOLO 分类建议、PaddleOCR 证件信息提取、CLIP 文图相似检索）。

系统目标是：让失主和拾到者更快完成匹配，同时兼顾证件类隐私保护（图片自动脱敏 + 敏感字段加密存储）。

---

## 系统展示图片

系统演示截图统一放在项目根目录 `show_images` 文件夹中。  
以下为当前已接入 README 的展示图：

### 登录与首页
![登录页面展示](./show_images/登录页面展示.png)
![首页搜索筛选展示](./show_images/首页搜索筛选展示.png)
![首页展示_寻物启事](./show_images/首页展示_寻物启事.png)
![首页展示_失物招领](./show_images/首页展示_失物招领.png)

### 发布与证件识别
![发布页面展示](./show_images/发布页面展示.png)
![发布页面_选择上传身份证_识别加文字提取展示](./show_images/发布页面_选择上传身份证_识别加文字提取展示.png)

### 文图搜与消息
![文图搜_文搜展示](./show_images/文图搜_文搜展示.png)
![文图搜_图搜展示](./show_images/文图搜_图搜展示.png)
![消息展示](./show_images/消息展示.png)

### 个人中心
![我的展示](./show_images/我的展示.png)

---

## 1. 核心能力

### 1.1 基础业务
- 用户注册/登录、个人资料维护
- 发布寻物/招领帖子（支持多图）
- 首页列表、详情页、我的发布
- 评论与回复通知
- 收藏与消息提醒
- 物品状态流转（未找回/已找回、未认领/已认领）

### 1.2 证件隐私能力
- 证件类（如身份证/学生证）上传后自动脱敏
- 规则：默认仅姓名可保留，其它字段优先打码
- OCR 自动提取姓名、证件号/学号、学院、专业、地址
- 敏感字段（证件号、地址等）加密入库，仅姓名可用于检索展示

### 1.3 AI 能力
- YOLO：发布阶段“识别首图并推荐分类”
- PaddleOCR：证件信息识别与结构化提取
- CLIP（`ViT-L-14-336`）：文搜/图搜智能匹配
- 特征入库：`item_feature` 向量表，用于加速检索

---

## 2. 技术架构

### 2.1 前端
- 微信小程序原生（WXML / WXSS / JS）
- 主要目录：`frontend/pages/*`
- 网络层：`frontend/utils/request.js`、`frontend/utils/api.js`

### 2.2 后端
- FastAPI + SQLAlchemy + MySQL
- 主要目录：`backend/app`
  - `api/v1`：接口层
  - `services`：业务与 AI 服务层
  - `repositories`：数据访问层
  - `models`：ORM 模型
  - `schemas`：请求/响应结构

### 2.3 AI 与模型
- YOLO：本地模型推理（CPU优先）
- PaddleOCR：证件字段识别
- Chinese-CLIP：文本-图像相似检索
- 统一由 `backend/app/services/ai_service.py`、`clip_service.py` 管理

---

## 3. 项目目录

```text
smart-campus-lnf/
├── frontend/                      # 微信小程序
│   ├── app.js
│   ├── pages/
│   │   ├── home/
│   │   ├── publish/
│   │   ├── item-detail/
│   │   ├── smart-search/
│   │   └── ...
│   └── utils/
├── backend/                       # FastAPI 后端
│   ├── main.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── api/v1/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   └── schemas/
│   ├── scripts/
│   └── uploads/                   # 上传与脱敏图片目录
├── yolo_model/                    # YOLO 权重目录
├── docs/                          # 设计与接口文档
└── README.md
```

---

## 4. 环境要求

- Python 3.10+
- MySQL 8.x
- 微信开发者工具（前端调试）
- Windows / Linux 均可（本项目已在 Windows 本地验证）

---

## 5. 快速启动

## 5.1 数据库准备

1. 创建数据库：`lostfound_db`
2. 导入项目 schema（见 `docs/03_database` 下脚本）
3. 确认账号可访问（默认示例：`root/123456`）

## 5.2 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8091
```

访问 Swagger：`http://127.0.0.1:8091/docs`

> 当前默认配置见 `backend/app/config.py`：
> - `base_url = http://127.0.0.1:8091`
> - `database_url = mysql+pymysql://root:123456@localhost:3306/lostfound_db?...`
> - `clip_model_name = ViT-L-14-336`

## 5.3 启动前端（微信小程序）

1. 微信开发者工具打开 `frontend` 目录
2. 勾选开发环境下“**不校验合法域名**”
3. 确认 `frontend/app.js` 指向后端地址（默认 `8091`）
4. 编译运行

---

## 6. 关键功能使用说明

## 6.1 发布流程（普通物品）
1. 进入发布页，选择“寻物”或“招领”
2. 上传图片并填写标题/描述/地点/联系方式
3. 可选点击“AI识别首图并推荐分类”
4. 提交后帖子写入数据库并在首页展示

## 6.2 发布流程（证件类）
1. 分类选择“证件”
2. 点击“证件OCR自动提取”
3. 页面按识别结果动态展示字段（姓名/学号/学院/专业等）
4. 核对后提交
5. 后端自动执行：
   - 图片脱敏（姓名尽量保留，敏感信息打码）
   - 敏感字段加密存储

## 6.3 智能文图搜
1. 进入“智能文图搜”页
2. 选择模式：文搜 / 图搜
3. 选择筛选：全部 / 只看寻物 / 只看招领
4. 执行搜索，查看匹配度结果并跳转详情

---

## 7. 主要接口（节选）

### 7.1 公共
- `POST /api/v1/common/upload`：上传图片
- `GET /api/v1/common/item-types`：物品类型列表

### 7.2 物品
- `GET /api/v1/items`：列表
- `POST /api/v1/items`：创建
- `GET /api/v1/items/{item_id}`：详情
- `PUT /api/v1/items/{item_id}/status`：更新状态

### 7.3 AI
- `POST /api/v1/ai/recognize/image`：YOLO识别图片分类建议
- `POST /api/v1/ai/ocr/id-card`：证件OCR提取
- `GET /api/v1/ai/health`：AI健康检查

### 7.4 搜索
- `POST /api/v1/search/by-image`：图搜
- `GET /api/v1/search/by-text`：文搜
- `GET /api/v1/search/health`：CLIP健康检查

---

## 8. 数据与隐私说明

- 证件类字段按“最小暴露”原则处理
- 图片层：自动脱敏后再用于前台展示
- 数据层：敏感字段加密存储（如证件号、地址）
- 检索层：姓名可用于检索，其它敏感值不用于公开展示

---

## 9. 常见问题（FAQ）

### Q1：前端请求失败？
- 检查后端是否运行在 `8091`
- 检查小程序是否关闭了域名校验
- 检查 `frontend/app.js` 的 `baseUrl/baseUrls`

### Q2：OCR没识别到字段？
- 优先使用证件正面清晰图
- 先看是否返回了 `ocr_error`
- 确认 Paddle 运行环境可用（`paddlepaddle + paddleocr`）

### Q3：文图搜没结果或结果少？
- 检查 CLIP 模型加载状态（`/api/v1/search/health`）
- 确认 `item_feature` 是否已回填
- 检查是否启用了“只看寻物/只看招领”筛选

---

## 10. 开发建议

- 生产环境建议将 `uploads` 迁移到对象存储（OSS/S3）
- 建议把模型下载目录做持久化挂载
- 可将 OCR/CLIP 推理拆成独立服务，避免主API阻塞
- 对关键任务（OCR、特征回填）增加异步队列与重试机制

---

## 11. 版本说明

当前 README 对应的是“AI增强版”实现：
- 支持证件OCR字段动态展示
- 支持证件脱敏与敏感字段加密
- 支持文搜/图搜与寻物/招领筛选
- 支持 CLIP 特征入库检索

---

