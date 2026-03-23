# 智能校园失物招领系统 - API 文档

> **版本**：v1.0  
> **更新日期**：2025-03-22  
> **关联**：PRD、数据库设计、流程图

---

## 一、概述

### 1.1 基础信息

| 项目 | 说明 |
|------|------|
| **Base URL** | `https://api.example.com/v1`（开发环境可替换为 `http://localhost:8080/api/v1`） |
| **数据格式** | JSON |
| **字符编码** | UTF-8 |

### 1.2 通用约定

- **请求头**：需登录的接口需携带 `Authorization: Bearer <token>`
- **分页**：`page` 从 1 开始，`page_size` 默认 10，最大 50
- **时间格式**：`YYYY-MM-DD HH:mm:ss` 或 ISO 8601

### 1.3 统一响应格式

**成功响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

**分页数据：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

**错误响应：**

```json
{
  "code": 40001,
  "message": "参数错误：标题不能为空",
  "data": null
}
```

**常用错误码：**

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 40001 | 参数错误 |
| 40100 | 未登录 |
| 40101 | Token 无效或过期 |
| 40300 | 无权限 |
| 40400 | 资源不存在 |
| 50000 | 服务器内部错误 |

---

## 二、认证相关

### 2.1 用户注册

**POST** `/auth/register`

**请求体：**

```json
{
  "username": "张三",
  "password": "password123",
  "phone": "13800138000",
  "student_id": "2024001"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，2-64 字符 |
| password | string | 是 | 密码，6-32 字符 |
| phone | string | 否 | 手机号，与 student_id 二选一 |
| student_id | string | 否 | 学号 |

**响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "张三",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

### 2.2 用户登录

**POST** `/auth/login`

**请求体：**

```json
{
  "account": "13800138000",
  "password": "password123"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| account | string | 是 | 手机号或学号 |
| password | string | 是 | 密码 |

**响应：** 同注册

### 2.3 刷新 Token（可选）

**POST** `/auth/refresh`

**请求头：** `Authorization: Bearer <token>`

**响应：** 返回新 token

---

## 三、用户相关

### 3.1 获取当前用户信息

**GET** `/user/profile` 🔒

**响应：**

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "张三",
    "phone": "138****8000",
    "student_id": "2024001",
    "avatar": "https://cdn.example.com/avatar/1.jpg",
    "created_at": "2025-03-01 10:00:00"
  }
}
```

### 3.2 更新用户信息

**PUT** `/user/profile` 🔒

**请求体：**

```json
{
  "username": "张三",
  "avatar": "https://cdn.example.com/avatar/1.jpg"
}
```

---

## 四、物品相关

### 4.1 发布物品（寻物/招领）

**POST** `/items` 🔒

**请求体（multipart/form-data 或 JSON + 图片 URL）：**

```json
{
  "item_type": 1,
  "title": "寻找丢失的钥匙串",
  "description": "一串蓝色钥匙扣，上有小挂件",
  "location_id": 1,
  "location_detail": "图书馆三楼阅览区靠窗",
  "lost_found_time": "2025-03-20 14:30:00",
  "contact_info": "13800138000",
  "images": [
    {
      "url": "https://cdn.example.com/item/1.jpg",
      "sort_order": 0
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| item_type | int | 是 | 1=寻物，2=招领 |
| title | string | 是 | 标题 |
| description | string | 否 | 描述 |
| location_id | long | 否 | 地点 ID |
| location_detail | string | 否 | 地点补充 |
| lost_found_time | string | 否 | 丢失/拾取时间 |
| contact_info | string | 否 | 联系方式 |
| images | array | 是 | 图片列表，至少 1 张 |

> **补充说明**：若采用「先上传图片再发布」流程，可先调用 `/ai/recognize` 获取识别结果，再在发布时传入 `item_type_id`、`ocr_text` 等；也可在发布接口内同步调用 AI 识别并自动补全。

**响应：**

```json
{
  "code": 0,
  "data": {
    "id": 100,
    "item_type": 1,
    "title": "寻找丢失的钥匙串",
    "status": 1,
    "created_at": "2025-03-22 10:00:00"
  }
}
```

### 4.2 获取物品列表（首页/浏览）

**GET** `/items`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| item_type | int | 否 | 1=寻物，2=招领 |
| status | int | 否 | 1/2/3，默认 1 |
| location_id | long | 否 | 按地点筛选 |
| item_type_id | long | 否 | 按物品类型筛选 |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页条数，默认 10 |

**响应：**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 100,
        "item_type": 1,
        "item_type_name": "钥匙",
        "title": "寻找丢失的钥匙串",
        "cover_image": "https://cdn.example.com/item/100.jpg",
        "location_name": "图书馆三楼",
        "lost_found_time": "2025-03-20 14:30:00",
        "status": 1,
        "created_at": "2025-03-22 10:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 10
  }
}
```

### 4.3 获取物品详情

**GET** `/items/:id`

**路径参数：** `id` - 物品 ID

**响应：**

```json
{
  "code": 0,
  "data": {
    "id": 100,
    "user_id": 1,
    "username": "张三",
    "avatar": "https://...",
    "item_type": 1,
    "item_type_name": "钥匙",
    "title": "寻找丢失的钥匙串",
    "description": "一串蓝色钥匙扣...",
    "status": 1,
    "location": {
      "id": 1,
      "name": "图书馆三楼",
      "longitude": 116.397128,
      "latitude": 39.916527
    },
    "location_detail": "阅览区靠窗",
    "lost_found_time": "2025-03-20 14:30:00",
    "contact_info": "138****8000",
    "view_count": 12,
    "images": [
      {
        "id": 1,
        "url": "https://cdn.example.com/item/100.jpg",
        "ocr_text": "校园卡 张三..."
      }
    ],
    "is_favorited": false,
    "created_at": "2025-03-22 10:00:00"
  }
}
```

> **补充说明**：调用此接口时应记录 `behavior_log`（view），用于协同过滤推荐。

### 4.4 更新物品状态

**PUT** `/items/:id/status` 🔒

**请求体：**

```json
{
  "status": 3
}
```

| status | 说明 |
|--------|------|
| 1 | 待认领/寻找中 |
| 2 | 沟通中 |
| 3 | 已归还 |

**权限**：仅发布者可修改

### 4.5 删除物品

**DELETE** `/items/:id` 🔒

**权限**：仅发布者可删除

---

## 五、搜索相关

### 5.1 以图搜图

**POST** `/search/by-image` 🔒（可选，未登录也可开放）

**请求体（multipart/form-data）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | file | 是 | 图片文件，支持 jpg/png |
| item_type | int | 否 | 1=寻物，2=招领，不传则全部 |
| top_n | int | 否 | 返回条数，默认 20 |

**响应：**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 100,
        "item_type": 1,
        "item_type_name": "钥匙",
        "title": "寻找丢失的钥匙串",
        "cover_image": "https://...",
        "similarity": 0.92,
        "location_name": "图书馆三楼",
        "lost_found_time": "2025-03-20 14:30:00",
        "status": 1
      }
    ]
  }
}
```

> **补充说明**：后端流程：接收图片 → YOLO 识别 → OCR 提取 → CLIP 生成向量 → 向量相似度检索 → 五维加权排序 → 返回结果。`similarity` 为综合相似度 0-1。

### 5.2 以文搜文

**GET** `/search/by-text` 

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| item_type | int | 否 | 1=寻物，2=招领 |
| location_id | long | 否 | 地点筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页条数 |

**响应：** 同 4.2 列表格式，按相关度排序

> **补充说明**：可结合 `item_image.ocr_text` 全文检索 + `item` 表关键词匹配，或使用 CLIP 文本编码后向量检索。

### 5.3 综合搜索（可选）

**POST** `/search` 

支持关键词 + 筛选条件组合，返回统一列表格式。

---

## 六、AI 相关

### 6.1 图片识别（YOLO + OCR）

**POST** `/ai/recognize`

**请求体（multipart/form-data）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | file | 是 | 图片文件 |

**响应：**

```json
{
  "code": 0,
  "data": {
    "yolo": {
      "item_type_id": 1,
      "item_type_name": "钥匙",
      "bbox": [100, 150, 300, 400]
    },
    "ocr": {
      "text": "校园卡 张三 2024001"
    }
  }
}
```

> **补充说明**：用于发布前「上传即识别」场景，前端拿到结果后自动填充表单。可与发布接口合并为一步。

### 6.2 相关失物推荐

**GET** `/items/:id/recommendations`

**路径参数：** `id` - 当前物品 ID

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| top_n | int | 否 | 返回条数，默认 10 |

**响应：**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 101,
        "item_type": 1,
        "title": "拾获钥匙一串",
        "cover_image": "https://...",
        "similarity": 0.88,
        "location_name": "教学楼A",
        "status": 1
      }
    ]
  }
}
```

> **补充说明**：五维加权排序（图像 40% + 文本 30% + 地点 20% + 时间 10% + 协同过滤）。权重从 `system_config` 读取。

---

## 七、消息相关

### 7.1 发送消息

**POST** `/messages` 🔒

**请求体：**

```json
{
  "to_user_id": 2,
  "item_id": 100,
  "content": "您好，这件物品可能是我丢失的，方便联系吗？"
}
```

### 7.2 获取消息列表

**GET** `/messages` 🔒

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页条数 |
| item_id | long | 否 | 按物品筛选 |
| with_user_id | long | 否 | 与某用户的会话 |

**响应：**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 1,
        "from_user_id": 2,
        "from_username": "李四",
        "to_user_id": 1,
        "item_id": 100,
        "item_title": "寻找丢失的钥匙串",
        "content": "您好，这件物品可能是我丢失的...",
        "is_read": 1,
        "is_self": false,
        "created_at": "2025-03-22 11:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 10
  }
}
```

### 7.3 标记已读

**PUT** `/messages/:id/read` 🔒

### 7.4 未读数量

**GET** `/messages/unread-count` 🔒

**响应：**

```json
{
  "code": 0,
  "data": {
    "count": 3
  }
}
```

---

## 八、收藏相关

### 8.1 收藏物品

**POST** `/favorites` 🔒

**请求体：**

```json
{
  "item_id": 100
}
```

### 8.2 取消收藏

**DELETE** `/favorites/:item_id` 🔒

### 8.3 我的收藏列表

**GET** `/favorites` 🔒

**Query 参数：** `page`, `page_size`

**响应：** 同 4.2 列表格式

---

## 九、公共接口

### 9.1 物品类型列表

**GET** `/common/item-types`

**响应：**

```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "name": "钥匙",
      "code": "key"
    },
    {
      "id": 2,
      "name": "钱包",
      "code": "wallet"
    }
  ]
}
```

### 9.2 地点列表

**GET** `/common/locations`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 地点名称模糊搜索 |
| campus | string | 否 | 按校区筛选 |

**响应：**

```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "name": "图书馆三楼",
      "campus": "本部",
      "building": "图书馆",
      "floor": "3",
      "longitude": 116.397128,
      "latitude": 39.916527
    }
  ]
}
```

### 9.3 图片上传

**POST** `/common/upload` 🔒

**请求体（multipart/form-data）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 图片文件 |

**响应：**

```json
{
  "code": 0,
  "data": {
    "url": "https://cdn.example.com/item/xxx.jpg"
  }
}
```

---

## 十、接口汇总

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 认证 | POST | /auth/register | 注册 |
| 认证 | POST | /auth/login | 登录 |
| 认证 | POST | /auth/refresh | 刷新 Token |
| 用户 | GET | /user/profile | 获取当前用户 |
| 用户 | PUT | /user/profile | 更新用户 |
| 物品 | POST | /items | 发布物品 |
| 物品 | GET | /items | 物品列表 |
| 物品 | GET | /items/:id | 物品详情 |
| 物品 | PUT | /items/:id/status | 更新状态 |
| 物品 | DELETE | /items/:id | 删除物品 |
| 物品 | GET | /items/:id/recommendations | 相关推荐 |
| 搜索 | POST | /search/by-image | 以图搜图 |
| 搜索 | GET | /search/by-text | 以文搜文 |
| AI | POST | /ai/recognize | 图片识别 |
| 消息 | POST | /messages | 发送消息 |
| 消息 | GET | /messages | 消息列表 |
| 消息 | PUT | /messages/:id/read | 标记已读 |
| 消息 | GET | /messages/unread-count | 未读数 |
| 收藏 | POST | /favorites | 收藏 |
| 收藏 | DELETE | /favorites/:item_id | 取消收藏 |
| 收藏 | GET | /favorites | 收藏列表 |
| 公共 | GET | /common/item-types | 物品类型 |
| 公共 | GET | /common/locations | 地点列表 |
| 公共 | POST | /common/upload | 图片上传 |

🔒 表示需登录

---

## 十一、附录

### 11.1 与数据库映射

| 接口 | 主要涉及表 |
|------|------------|
| 发布物品 | item, item_image, item_feature, recognition_log |
| 以图搜图 | item_feature, item, item_image |
| 相关推荐 | item_feature, behavior_log, item |
| 消息 | message |

### 11.2 补充说明

- **Base URL**、**Token 机制**（JWT/session）可根据实际技术选型调整
- **图片上传**：可先上传至 OSS 再传 URL，或直接 multipart 上传由后端存储
- **以图搜图**：若使用向量库，检索逻辑在应用层调用向量库 API，本文档仅描述对外接口
- **限流**：建议对搜索、AI 识别等接口做限流，防止滥用
