# 智能校园失物招领系统（Smart Campus Lost & Found）

面向高校场景的一体化失物招领平台，覆盖「发布 - 检索 - 匹配 - 通知 - 处理 - 关闭」完整闭环。  
系统基于微信小程序 + FastAPI + MySQL 构建，融合 AI 检索与隐私保护能力，提升失物找回效率并降低人工沟通成本。

---

## 完整演示

> 演示截图统一放在项目根目录 `show_images/`。  
> 按“登录首页 → 发布 → 文图搜 → 消息 → 我的”完整业务链路展示。

### 1) 登录与首页

**说明：**
- 登录页支持微信一键登录，已登录用户自动校验并直达首页。
- 首页提供“寻物启事 / 失物招领”双列表，支持关键词、分类、地点联合筛选。
- 首页卡片展示标题、地点、时间、状态，支持进入详情与评论互动。

**用法：**
1. 打开小程序完成微信登录。
2. 在首页输入关键词或切换分类进行筛选。
3. 点击地点按钮选择校园地点，按地点过滤结果。
4. 点击“取消筛选”可一键恢复默认展示。

<p align="left">
  <img src="./show_images/登录页面展示.png" alt="登录页面展示" width="23%" />
  <img src="./show_images/首页展示_寻物启事.png" alt="首页展示_寻物启事" width="23%" />
  <img src="./show_images/首页展示_失物招领.png" alt="首页展示_失物招领" width="23%" />
  <img src="./show_images/校园地点展示.png" alt="校园地点展示" width="23%" />
  <img src="./show_images/首页搜索筛选展示1.png" alt="首页搜索筛选展示1" width="23%" />
  <img src="./show_images/首页搜索筛选展示2.png" alt="首页搜索筛选展示2" width="23%" />
  <img src="./show_images/卡片详情页.png" alt="卡片详情页" width="23%" />
</p>

### 2) 发布与证件识别

**说明：**
- 发布页支持寻物/招领双模式、多图上传、AI 首图分类建议。
- 证件类支持 OCR 自动提取字段，并采用动态字段展示降低手填成本。
- 证件信息提交后执行隐私保护流程（图片脱敏 + 敏感字段加密）。

**用法：**
1. 进入发布页，选择“寻物”或“招领”。
2. 上传图片并填写标题、描述、地点、联系方式。
3. 若为证件类，点击“证件OCR自动提取”并核对识别结果。
4. 提交后系统会自动触发匹配扫描，并在命中时发送站内匹配通知。

<p align="left">
  <img src="./show_images/发布页面展示.png" alt="发布页面展示" width="23%" />
  <img src="./show_images/发布页面_选择上传身份证_识别加文字提取展示.png" alt="发布页面_选择上传身份证_识别加文字提取展示" width="23%" />
</p>

### 3) 文图搜

**说明：**
- 智能搜索支持文搜与图搜两种模式，基于 CLIP 相似度返回 Top-K。
- 支持“全部 / 只看寻物 / 只看招领”筛选，便于按场景精准检索。
- 可与首页筛选、详情页推荐互补使用，提升找回效率。

**用法：**
1. 进入“文图搜”，选择文搜或图搜模式。
2. 输入文本描述或上传待检索图片。
3. 按需切换检索范围（全部、寻物、招领）。
4. 点击结果卡片进入详情，继续留言或联系发布者。

<p align="left">
  <img src="./show_images/文图搜_文搜展示.png" alt="文图搜_文搜展示" width="23%" />
  <img src="./show_images/文图搜_图搜展示.png" alt="文图搜_图搜展示" width="23%" />
  <img src="./show_images/文搜展示1.png" alt="文搜展示1" width="23%" />
</p>

### 4) 消息中心

**说明：**
- 消息中心分为系统通知、匹配通知、回复通知三类，未读数量动态展示。
- 匹配通知来源于“发布后即时匹配 + 每日自动重扫匹配”双机制。
- 进入分类页会自动标记该分类消息已读，便于统一管理。

**用法：**
1. 在底部导航点击“消息”进入消息中心。
2. 选择对应分类查看消息详情。
3. 点击消息可跳转到关联帖子继续处理（评论、联系、更新状态）。

<p align="left">
  <img src="./show_images/消息展示.png" alt="消息展示" width="23%" />
  <img src="./show_images/消息展示_匹配通知.png" alt="消息展示_匹配通知" width="23%" />
  <img src="./show_images/消息展示_回复通知.png" alt="消息展示_回复通知" width="23%" />
</p>

### 5) 个人中心

**说明：**
- 个人中心展示真实业务统计：发布失物、已找回、发布招领、获赞。
- 支持“我的寻物/我的招领/已找回记录”卡片化管理。
- “校园好市民”采用动态积分等级体系，并支持资料编辑与退出登录。

**用法：**
1. 点击底部导航“我的”进入个人中心。
2. 查看个人统计与等级进度，进入我的发布管理状态。
3. 在“修改资料”完善学院、专业、年级等信息。
4. 通过“退出登录”返回登录页进行账号切换或登录流程测试。

<p align="left">
  <img src="./show_images/我的展示.png" alt="我的展示" width="23%" />
  <img src="./show_images/我的寻物展示.png" alt="我的寻物展示" width="23%" />
  <img src="./show_images/我的招领展示.png" alt="我的招领展示" width="23%" />
  <img src="./show_images/我的发布状态修改展示.png" alt="我的发布状态修改展示" width="23%" />
  <img src="./show_images/修改资料展示.png" alt="修改资料展示" width="23%" />
</p>

---

## 项目定位

本系统不只是“信息公告板”，而是可持续运行的校园服务平台：

- 为失主提供更快找到物品的路径（文搜/图搜 + 推荐 + 自动匹配通知）
- 为拾获者提供更低成本的发布流程（AI 分类建议 + OCR 辅助填写）
- 为学校提供更规范的隐私治理能力（证件脱敏 + 敏感字段加密）
- 为运营提供自动化机制（每周提醒 + 到期自动关闭 + 每日自动重扫匹配）

---

## 核心功能与特色

### 1) 双业务链路闭环

- **寻物启事**：失主发布丢失信息，等待匹配与线索
- **失物招领**：拾获者发布招领信息，等待失主认领
- **状态流转**：未找回/已找回/已关闭、未认领/已认领/已关闭
- **评论互动**：围绕帖子进行线索交流，自动生成回复通知

### 2) 智能搜索与推荐

- **文搜 / 图搜**：基于 CLIP 向量相似度返回 Top-K 结果
- **相关推荐**：融合内容相似（CLIP）与行为协同（收藏/浏览/评论等）输出相关物品
- **发布后即时匹配**：新帖创建后自动触发匹配扫描并生成匹配通知
- **每日自动重扫匹配**：即使用户离线，系统每天也会重扫未关闭帖子并补发站内通知

### 3) 智能发布与 AI 辅助

- **YOLO 首图分类建议**：发布时自动给出分类建议，可辅助填表
- **证件 OCR 提取**：自动识别姓名、学号/证件号、学院、专业、地址等字段
- **动态字段展示**：证件类“先识别再展示”，减少手填负担

### 4) 隐私安全与合规设计

- **图片脱敏**：证件图片优先打码，尽量仅保留必要可见信息
- **敏感字段加密入库**：证件号/地址等敏感信息加密存储
- **最小暴露原则**：公开端仅展示业务必要字段，避免敏感数据泄露

### 5) 消息中心与自动化运营

- **消息分类**：系统通知、匹配通知、回复通知分栏展示
- **已读策略**：进入分类页自动批量标记已读
- **每周提醒**：系统每周提醒用户确认帖子状态
- **四周自动关闭**：超期未处理帖子自动关闭，保持列表有效性

### 6) 用户中心能力

- **真实数据看板**：发布失物、已找回、发布招领、获赞等均为数据库实时统计
- **我的发布卡片化管理**：我的寻物/我的招领/已找回记录均为卡片流展示
- **信誉等级体系（校园好市民）**：基于真实行为积分动态计算等级与进度
- **退出登录**：支持从“我的”页面主动退出并返回登录页

### 7) 校园场景适配

- **校园地点库**：内置食堂、宿舍、校门、图书馆、运动场、景点、教室位置
- **地点选择器**：发布时按校园地点结构化选择
- **地点筛选**：首页可按地点筛选并一键取消筛选恢复默认状态

---

## 技术架构

### 前端（微信小程序）

- 技术栈：WXML / WXSS / JavaScript
- 关键模块：
  - `frontend/pages/home`：首页、筛选、地点筛选
  - `frontend/pages/publish`：发布、AI建议、OCR、地点选择
  - `frontend/pages/smart-search`：文搜/图搜
  - `frontend/pages/message/*`：消息中心
  - `frontend/pages/profile`：个人中心与等级
  - `frontend/pages/location-picker`：校园地点选择器
- 网络层：`frontend/utils/request.js`、`frontend/utils/api.js`

### 后端（FastAPI）

- 技术栈：FastAPI + SQLAlchemy + MySQL
- 分层结构：
  - `api/v1`：接口层
  - `services`：业务逻辑、AI、匹配、定时任务
  - `repositories`：数据访问层
  - `models`：ORM 数据模型
  - `schemas`：请求/响应结构
- 关键服务：
  - `clip_service.py`：CLIP 编码、检索、特征写入
  - `match_notify_service.py`：匹配通知（>=90%）
  - `recommend_service.py`：推荐融合（内容 + 协同过滤）
  - `scheduler_service.py`：每周/每日自动任务调度

### AI 能力

- YOLO：图片分类建议
- PaddleOCR：证件字段识别
- Chinese-CLIP：文图统一向量检索与相似度计算

---

## 项目目录

```text
smart-campus-lnf/
├── frontend/                      # 微信小程序端
│   ├── app.js
│   ├── pages/
│   └── utils/
├── backend/                       # FastAPI 后端
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── api/v1/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   └── schemas/
│   ├── scripts/
│   └── uploads/
├── show_images/                   # README 演示截图
├── yolo_model/                    # YOLO 权重
├── docs/
└── README.md
```

---

## 运行环境

- Python 3.10+
- MySQL 8.x
- 微信开发者工具
- Windows / Linux（本项目已在 Windows 环境验证）

---

## 快速启动

### 1) 数据库准备

1. 创建数据库：`lostfound_db`
2. 导入建表脚本（参考 `docs/03_database`）
3. 确认账号可访问

### 2) 配置后端环境变量

在 `backend/.env` 中至少配置：

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/lostfound_db?charset=utf8mb4
BASE_URL=http://127.0.0.1:8091
WECHAT_APPID=你的小程序AppID
WECHAT_SECRET=你的小程序Secret
```

可选（定时任务相关）：

```env
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Shanghai
SCHEDULER_WEEKLY_DAY_OF_WEEK=mon
SCHEDULER_WEEKLY_HOUR=9
SCHEDULER_WEEKLY_MINUTE=0
SCHEDULER_DAILY_MATCH_HOUR=9
SCHEDULER_DAILY_MATCH_MINUTE=30
```

### 3) 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8091
```

接口文档：`http://127.0.0.1:8091/docs`

### 4) 启动前端

1. 微信开发者工具打开 `frontend/`
2. 开发阶段关闭域名校验
3. 检查 `frontend/app.js` 的后端地址指向 `8091`
4. 编译运行

---

## 关键业务流程

### A. 普通物品发布流程

1. 选择“寻物”或“招领”
2. 上传图片，填写标题/描述/地点/联系方式
3. 可选使用 AI 分类建议
4. 发布成功后写入数据库并触发匹配扫描

### B. 证件类发布流程

1. 选择“证件”分类
2. 点击 OCR 自动提取
3. 核对并补全识别字段
4. 提交后自动执行脱敏与敏感字段加密

### C. 自动通知流程

1. 发布后即时匹配（>=90%） -> 生成匹配消息
2. 每日任务重扫未关闭寻物帖 -> 补发匹配消息
3. 每周任务提醒确认状态
4. 四周超期帖子自动关闭

---

## 主要接口（节选）

### 认证

- `POST /api/v1/auth/wechat-login`：微信登录
- `GET /api/v1/auth/me`：当前用户信息
- `GET /api/v1/auth/me/stats`：个人中心统计数据

### 物品

- `GET /api/v1/items`：首页列表
- `POST /api/v1/items`：发布帖子
- `GET /api/v1/items/mine`：我的发布（支持状态筛选）
- `PUT /api/v1/items/{item_id}/status`：修改状态
- `POST /api/v1/items/{item_id}/match-notify`：手动触发匹配

### 搜索与推荐

- `GET /api/v1/search/by-text`：文搜
- `POST /api/v1/search/by-image`：图搜
- `GET /api/v1/items/{item_id}/recommendations`：相关推荐
- `POST /api/v1/recommend/events`：行为埋点

### AI 与公共能力

- `POST /api/v1/ai/recognize/image`：AI分类建议
- `POST /api/v1/ai/ocr/id-card`：证件OCR
- `POST /api/v1/common/upload`：上传图片
- `GET /api/v1/common/login-stats`：登录页动态统计

---

## 数据安全与隐私

- 证件信息遵循“最小可见”原则
- 图片展示优先使用脱敏版本
- 敏感字段加密后入库
- 消息与检索不暴露敏感明文

---

## 常见问题（FAQ）

### Q1：微信登录返回 503（未配置）？

请检查 `backend/.env` 是否配置了：

- `WECHAT_APPID`
- `WECHAT_SECRET`

并重启后端。

### Q2：图片不显示或显示默认图？

- 检查 `BASE_URL` 与上传 URL 是否一致
- 检查 `backend/uploads` 中是否有对应文件
- 检查后端是否单实例运行（避免旧进程返回旧字段）

### Q3：图搜/文搜结果异常？

- 访问 `/api/v1/search/health` 检查 CLIP 状态
- 检查 `item_feature` 特征是否已写入
- 确认筛选条件（寻物/招领/地点）是否过严

### Q4：匹配通知没出现？

- 确认匹配阈值逻辑（图片相似度 >= 90%）
- 确认消息页是否查看“匹配通知”分类
- 可调用 `POST /api/v1/items/{id}/match-notify` 手动触发排查

---

## 版本亮点（当前实现）

- 微信一键登录 + 自动校验登录态
- 首页关键词 + 分类 + 地点筛选 + 一键取消筛选
- 发布页校园地点选择器（结构化地点库）
- 文搜/图搜 + 推荐系统 + 协同过滤埋点
- 匹配通知即时触发 + 每日自动重扫
- 每周提醒 + 四周自动关闭
- 证件 OCR + 图片脱敏 + 敏感字段加密
- 个人中心真实统计 + 校园好市民动态等级

