# 失物招领系统 RESTful API 协同接口文档

---

# 1. 文档说明

## 1.1 项目名称
校园失物招领系统

## 1.2 接口风格
RESTful API

## 1.3 数据格式
- 请求格式：`application/json`
- 响应格式：`application/json`

## 1.4 字符编码
- UTF-8

## 1.5 基础路径

```http
/api/v1
```
(注意，v1表示这是第一版，后面定了可能就不要/v1了)
例如：

```http
GET /api/v1/users/1
```

---

# 2. 通用约定

---

## 2.1 通用响应结构

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 业务状态码，0 表示成功 |
| message | string | 响应消息 |
| data | object/array/null | 响应数据 |

---

## 2.2 分页响应结构

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "pageNum": 1,
    "pageSize": 10,
    "total": 100
  }
}
```

---

## 2.3 常用业务状态码建议

| code | 含义 |
|---|---|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或 token 无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 数据冲突 |
| 500 | 服务器内部错误 |

---

## 2.4 认证方式

采用 `Bearer Token` 方式。

请求头示例：

```http
Authorization: Bearer <token>
```

---

# 3. 枚举值建议

以下是前后端联调时建议统一的状态值。

---

## 3.1 用户角色 `role`

| 值 | 含义 |
|---|---|
| user | 普通用户 |
| admin | 管理员 |

---

## 3.2 用户状态 `status`

| 值 | 含义 |
|---|---|
| enabled | 正常 |
| disabled | 禁用 |

---

## 3.3 失物/招领信息业务状态 `status`

| 值 | 含义 |
|---|---|
| published | 已发布 |
| closed | 已结束 |
| deleted | 已删除 |

---

## 3.4 审核状态 `audit_status`

| 值 | 含义 |
|---|---|
| pending | 待审核 |
| approved | 审核通过 |
| rejected | 审核拒绝 |

---

## 3.5 认领申请状态 `CLAIM_APPLICATION.status`

| 值 | 含义 |
|---|---|
| pending | 待处理 |
| approved | 已通过 |
| rejected | 已拒绝 |
| cancelled | 已取消 |

---

## 3.6 通知是否已读 `is_read`

| 值 | 含义 |
|---|---|
| true | 已读 |
| false | 未读 |

---

## 3.7 匹配状态 `MATCH_RECORD.status`

| 值 | 含义 |
|---|---|
| pending | 待确认 |
| matched | 已匹配 |
| ignored | 已忽略 |

---

# 4. 认证模块

---

## 4.1 用户注册

### 接口
```http
POST /api/v1/auth/register
```

### 请求参数

```json
{
  "studentNo": "20230001",
  "nickname": "小明",
  "realName": "张三",
  "phone": "13800000000",
  "email": "test@example.com",
  "password": "123456"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "id": 1
  }
}
```

---

## 4.2 用户登录

### 接口
```http
POST /api/v1/auth/login
```

### 请求参数

```json
{
  "studentNo": "20230001",
  "password": "123456"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "xxxxx.yyyyy.zzzzz",
    "userInfo": {
      "id": 1,
      "studentNo": "20230001",
      "nickname": "小明",
      "realName": "张三",
      "role": "user",
      "status": "enabled"
    }
  }
}
```

---

## 4.3 获取当前登录用户信息

### 接口
```http
GET /api/v1/auth/me
```

### 请求头
```http
Authorization: Bearer <token>
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "studentNo": "20230001",
    "nickname": "小明",
    "realName": "张三",
    "phone": "13800000000",
    "email": "test@example.com",
    "avatarUrl": "/upload/avatar/a.jpg",
    "role": "user",
    "status": "enabled",
    "createdAt": "2025-01-01 10:00:00"
  }
}
```

---

## 4.4 退出登录

### 接口
```http
POST /api/v1/auth/logout
```

### 响应示例

```json
{
  "code": 0,
  "message": "退出成功",
  "data": null
}
```

---

# 5. 用户模块

---

## 5.1 获取用户详情

### 接口
```http
GET /api/v1/users/{id}
```

### 路径参数

| 参数 | 类型 | 说明 |
|---|---|---|
| id | long | 用户ID |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "studentNo": "20230001",
    "nickname": "小明",
    "realName": "张三",
    "phone": "13800000000",
    "email": "test@example.com",
    "avatarUrl": "/upload/avatar/a.jpg",
    "role": "user",
    "status": "enabled",
    "createdAt": "2025-01-01 10:00:00",
    "updatedAt": "2025-01-02 11:00:00"
  }
}
```

---

## 5.2 更新个人信息

### 接口
```http
PUT /api/v1/users/{id}
```

### 请求参数

```json
{
  "nickname": "小明同学",
  "realName": "张三",
  "phone": "13800000001",
  "email": "new@example.com",
  "avatarUrl": "/upload/avatar/b.jpg"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "更新成功",
  "data": null
}
```

---

## 5.3 用户列表（管理员）

### 接口
```http
GET /api/v1/users
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |
| keyword | string | 否 | 学号/昵称/姓名关键词 |
| role | string | 否 | 用户角色 |
| status | string | 否 | 用户状态 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "studentNo": "20230001",
        "nickname": "小明",
        "realName": "张三",
        "phone": "13800000000",
        "role": "user",
        "status": "enabled",
        "createdAt": "2025-01-01 10:00:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "total": 1
  }
}
```

---

# 6. 物品分类模块

---

## 6.1 获取分类列表

### 接口
```http
GET /api/v1/categories
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| parentId | long | 否 | 父分类ID |
| status | string | 否 | 分类状态 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "parentId": 0,
      "name": "电子产品",
      "sortOrder": 1,
      "status": "enabled",
      "createdAt": "2025-01-01 10:00:00"
    }
  ]
}
```

---

## 6.2 新增分类（管理员）

### 接口
```http
POST /api/v1/categories
```

### 请求参数

```json
{
  "parentId": 0,
  "name": "证件卡类",
  "sortOrder": 2,
  "status": "enabled"
}
```

---

## 6.3 修改分类（管理员）

### 接口
```http
PUT /api/v1/categories/{id}
```

---

## 6.4 删除分类（管理员）

### 接口
```http
DELETE /api/v1/categories/{id}
```

---

# 7. 校园地点模块

---

## 7.1 获取地点列表

### 接口
```http
GET /api/v1/locations
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| campusName | string | 否 | 校区名称 |
| buildingName | string | 否 | 楼宇名称 |
| keyword | string | 否 | 地点关键词 |
| status | string | 否 | 地点状态 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "campusName": "主校区",
      "buildingName": "图书馆",
      "placeName": "一楼大厅",
      "longitude": 120.123456,
      "latitude": 30.123456,
      "description": "图书馆入口处",
      "status": "enabled",
      "createdAt": "2025-01-01 10:00:00"
    }
  ]
}
```

---

## 7.2 新增地点（管理员）

### 接口
```http
POST /api/v1/locations
```

### 请求参数

```json
{
  "campusName": "主校区",
  "buildingName": "图书馆",
  "placeName": "一楼大厅",
  "longitude": 120.123456,
  "latitude": 30.123456,
  "description": "图书馆入口处",
  "status": "enabled"
}
```

---

## 7.3 修改地点（管理员）

### 接口
```http
PUT /api/v1/locations/{id}
```

---

## 7.4 删除地点（管理员）

### 接口
```http
DELETE /api/v1/locations/{id}
```

---

# 8. 失物信息模块

---

## 8.1 发布失物信息

### 接口
```http
POST /api/v1/lost-items
```

### 请求参数

```json
{
  "categoryId": 1,
  "title": "丢失黑色双肩包",
  "description": "包内有笔记本电脑和学生证",
  "lostTime": "2025-01-10 15:30:00",
  "lostLocationId": 1,
  "lostLocationText": "图书馆二楼自习区",
  "contactPhone": "13800000000",
  "rewardInfo": "酬谢100元"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "发布成功",
  "data": {
    "id": 1001
  }
}
```

---

## 8.2 获取失物列表

### 接口
```http
GET /api/v1/lost-items
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |
| keyword | string | 否 | 标题/描述关键词 |
| categoryId | long | 否 | 分类ID |
| publisherId | long | 否 | 发布人ID |
| status | string | 否 | 业务状态 |
| auditStatus | string | 否 | 审核状态 |
| lostLocationId | long | 否 | 地点ID |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1001,
        "publisherId": 1,
        "categoryId": 1,
        "title": "丢失黑色双肩包",
        "description": "包内有笔记本电脑和学生证",
        "lostTime": "2025-01-10 15:30:00",
        "lostLocationId": 1,
        "lostLocationText": "图书馆二楼自习区",
        "contactPhone": "13800000000",
        "rewardInfo": "酬谢100元",
        "status": "published",
        "auditStatus": "pending",
        "viewCount": 12,
        "createdAt": "2025-01-10 16:00:00",
        "updatedAt": "2025-01-10 16:00:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "total": 1
  }
}
```

---

## 8.3 获取失物详情

### 接口
```http
GET /api/v1/lost-items/{id}
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1001,
    "publisherId": 1,
    "categoryId": 1,
    "title": "丢失黑色双肩包",
    "description": "包内有笔记本电脑和学生证",
    "lostTime": "2025-01-10 15:30:00",
    "lostLocationId": 1,
    "lostLocationText": "图书馆二楼自习区",
    "contactPhone": "13800000000",
    "rewardInfo": "酬谢100元",
    "status": "published",
    "auditStatus": "approved",
    "viewCount": 13,
    "createdAt": "2025-01-10 16:00:00",
    "updatedAt": "2025-01-10 16:10:00"
  }
}
```

---

## 8.4 修改失物信息

### 接口
```http
PUT /api/v1/lost-items/{id}
```

### 请求参数
同发布接口。

---

## 8.5 删除失物信息

### 接口
```http
DELETE /api/v1/lost-items/{id}
```

---

## 8.6 审核失物信息（管理员）

### 接口
```http
POST /api/v1/lost-items/{id}/audit
```

### 请求参数

```json
{
  "auditResult": "approved",
  "auditComment": "信息完整，审核通过"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "审核成功",
  "data": null
}
```

---

# 9. 招领信息模块

---

## 9.1 发布招领信息

### 接口
```http
POST /api/v1/found-items
```

### 请求参数

```json
{
  "categoryId": 2,
  "title": "拾到一张校园卡",
  "description": "在食堂门口捡到，卡面姓名可见",
  "foundTime": "2025-01-11 12:00:00",
  "foundLocationId": 2,
  "foundLocationText": "第一食堂门口",
  "pickupStoragePlace": "宿舍3号楼门卫室",
  "contactPhone": "13800000001"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "发布成功",
  "data": {
    "id": 2001
  }
}
```

---

## 9.2 获取招领列表

### 接口
```http
GET /api/v1/found-items
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |
| keyword | string | 否 | 标题/描述关键词 |
| categoryId | long | 否 | 分类ID |
| publisherId | long | 否 | 发布人ID |
| status | string | 否 | 业务状态 |
| auditStatus | string | 否 | 审核状态 |
| foundLocationId | long | 否 | 地点ID |

---

## 9.3 获取招领详情

### 接口
```http
GET /api/v1/found-items/{id}
```

---

## 9.4 修改招领信息

### 接口
```http
PUT /api/v1/found-items/{id}
```

---

## 9.5 删除招领信息

### 接口
```http
DELETE /api/v1/found-items/{id}
```

---

## 9.6 审核招领信息（管理员）

### 接口
```http
POST /api/v1/found-items/{id}/audit
```

### 请求参数

```json
{
  "auditResult": "rejected",
  "auditComment": "信息描述不完整，请补充"
}
```

---

# 10. 匹配记录模块

---

## 10.1 获取匹配记录列表

### 接口
```http
GET /api/v1/match-records
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |
| lostItemId | long | 否 | 失物ID |
| foundItemId | long | 否 | 招领ID |
| status | string | 否 | 匹配状态 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "lostItemId": 1001,
        "foundItemId": 2001,
        "matchScore": 0.92,
        "imageScore": 0.80,
        "textScore": 0.95,
        "locationScore": 0.90,
        "timeScore": 0.85,
        "matchReason": "标题、地点和时间高度相似",
        "status": "pending",
        "createdAt": "2025-01-11 13:00:00",
        "updatedAt": "2025-01-11 13:00:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "total": 1
  }
}
```

---

## 10.2 新增匹配记录

### 接口
```http
POST /api/v1/match-records
```

### 请求参数

```json
{
  "lostItemId": 1001,
  "foundItemId": 2001,
  "matchScore": 0.92,
  "imageScore": 0.80,
  "textScore": 0.95,
  "locationScore": 0.90,
  "timeScore": 0.85,
  "matchReason": "标题、地点和时间高度相似",
  "status": "pending"
}
```

---

## 10.3 修改匹配状态

### 接口
```http
PUT /api/v1/match-records/{id}
```

### 请求参数

```json
{
  "status": "matched"
}
```

---

## 10.4 删除匹配记录

### 接口
```http
DELETE /api/v1/match-records/{id}
```

---

# 11. 认领申请模块

---

## 11.1 提交认领申请

### 接口
```http
POST /api/v1/claim-applications
```

### 请求参数

```json
{
  "foundItemId": 2001,
  "claimDescription": "这是我的校园卡，卡号后四位是1234",
  "evidenceInfo": "可提供学号、身份证明",
  "contactPhone": "13800000002"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "提交成功",
  "data": {
    "id": 3001
  }
}
```

---

## 11.2 获取认领申请列表

### 接口
```http
GET /api/v1/claim-applications
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |
| foundItemId | long | 否 | 招领信息ID |
| claimUserId | long | 否 | 认领用户ID |
| status | string | 否 | 申请状态 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 3001,
        "foundItemId": 2001,
        "claimUserId": 3,
        "claimDescription": "这是我的校园卡，卡号后四位是1234",
        "evidenceInfo": "可提供学号、身份证明",
        "contactPhone": "13800000002",
        "status": "pending",
        "reviewComment": null,
        "createdAt": "2025-01-11 14:00:00",
        "updatedAt": "2025-01-11 14:00:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "total": 1
  }
}
```

---

## 11.3 获取认领申请详情

### 接口
```http
GET /api/v1/claim-applications/{id}
```

---

## 11.4 审核认领申请

### 接口
```http
POST /api/v1/claim-applications/{id}/review
```

### 请求参数

```json
{
  "status": "approved",
  "reviewComment": "核验信息一致，同意认领"
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "处理成功",
  "data": null
}
```

---

## 11.5 取消认领申请

### 接口
```http
POST /api/v1/claim-applications/{id}/cancel
```

### 响应示例

```json
{
  "code": 0,
  "message": "取消成功",
  "data": null
}
```

---

# 12. 通知模块

---

## 12.1 获取通知列表

### 接口
```http
GET /api/v1/notifications
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |
| type | string | 否 | 通知类型 |
| isRead | boolean | 否 | 是否已读 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "userId": 1,
        "type": "claim_result",
        "title": "认领申请审核结果",
        "content": "您的认领申请已通过，请尽快联系拾主。",
        "bizType": "claim_application",
        "bizId": 3001,
        "isRead": false,
        "createdAt": "2025-01-11 15:00:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "total": 1
  }
}
```

---

## 12.2 标记通知已读

### 接口
```http
POST /api/v1/notifications/{id}/read
```

### 响应示例

```json
{
  "code": 0,
  "message": "已标记为已读",
  "data": null
}
```

---

## 12.3 全部标记已读

### 接口
```http
POST /api/v1/notifications/read-all
```

### 响应示例

```json
{
  "code": 0,
  "message": "全部已读",
  "data": null
}
```

---

# 13. 审核记录模块

---

## 13.1 获取审核记录列表

### 接口
```http
GET /api/v1/audit-records
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |
| bizType | string | 否 | 业务类型 |
| bizId | long | 否 | 业务对象ID |
| auditorId | long | 否 | 审核人ID |
| auditResult | string | 否 | 审核结果 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "bizType": "lost_item",
        "bizId": 1001,
        "auditorId": 2,
        "auditResult": "approved",
        "auditComment": "内容属实，审核通过",
        "createdAt": "2025-01-10 18:00:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "total": 1
  }
}
```

---

## 13.2 获取某业务对象审核记录

### 接口
```http
GET /api/v1/audit-records/biz
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | string | 是 | 业务类型 |
| bizId | long | 是 | 业务对象ID |

---

# 14. 字段映射说明

为了方便前后端联调，建议接口字段使用 **camelCase**，数据库字段保持 **snake_case**。

例如：

| 数据库字段 | 接口字段 |
|---|---|
| student_no | studentNo |
| real_name | realName |
| password_hash | passwordHash |
| avatar_url | avatarUrl |
| parent_id | parentId |
| sort_order | sortOrder |
| campus_name | campusName |
| building_name | buildingName |
| place_name | placeName |
| lost_time | lostTime |
| lost_location_id | lostLocationId |
| lost_location_text | lostLocationText |
| contact_phone | contactPhone |
| reward_info | rewardInfo |
| audit_status | auditStatus |
| view_count | viewCount |
| found_time | foundTime |
| found_location_id | foundLocationId |
| found_location_text | foundLocationText |
| pickup_storage_place | pickupStoragePlace |
| lost_item_id | lostItemId |
| found_item_id | foundItemId |
| match_score | matchScore |
| image_score | imageScore |
| text_score | textScore |
| location_score | locationScore |
| time_score | timeScore |
| match_reason | matchReason |
| claim_user_id | claimUserId |
| claim_description | claimDescription |
| evidence_info | evidenceInfo |
| review_comment | reviewComment |
| user_id | userId |
| is_read | isRead |
| biz_type | bizType |
| auditor_id | auditorId |
| audit_result | auditResult |
| audit_comment | auditComment |
| created_at | createdAt |
| updated_at | updatedAt |

---

# 15. 联调建议

---

## 15.1 时间格式
统一使用：

```text
yyyy-MM-dd HH:mm:ss
```

例如：

```text
2025-01-11 14:00:00
```

---

## 15.2 ID 类型
所有主键、外键统一使用 `long / bigint`。

---

## 15.3 删除策略
建议业务上采用**逻辑删除**，接口层仍可保留 `DELETE` 语义。

---

## 15.4 权限建议
- 普通用户：
  - 注册、登录
  - 发布/修改自己的失物和招领信息
  - 提交和查看自己的认领申请
  - 查看和处理自己的通知
- 管理员：
  - 分类、地点管理
  - 审核失物/招领信息
  - 查看全部用户、认领申请、审核记录
  - 管理匹配记录

---

# 16. 推荐的通知类型 `NOTIFICATION.type`

| 值 | 含义 |
|---|---|
| audit_result | 审核结果通知 |
| claim_result | 认领处理结果通知 |
| claim_received | 收到认领申请通知 |
| match_reminder | 匹配提醒 |
| system | 系统通知 |

---

# 17. 推荐的业务类型 `biz_type`

| 值 | 含义 |
|---|---|
| lost_item | 失物信息 |
| found_item | 招领信息 |
| claim_application | 认领申请 |
| match_record | 匹配记录 |
