# 智能校园失物招领系统 - 数据字典

> **版本**：v1.0  
> **更新日期**：2025-03-22  
> **关联**：`schema.sql` 建表脚本

---

## 一、表清单总览


| 序号  | 表名              | 中文名   | 说明                 |
| --- | --------------- | ----- | ------------------ |
| 1   | user            | 用户表   | 用户账号、基础信息          |
| 2   | location        | 地点表   | 校园地点，支持 LBS        |
| 3   | item_type       | 物品类型表 | YOLO 识别类别          |
| 4   | item            | 物品表   | 失物/招领主表            |
| 5   | item_image      | 物品图片表 | 图片及 OCR、YOLO 结果    |
| 6   | item_feature    | 物品特征表 | CLIP 向量            |
| 7   | message         | 消息表   | 站内消息               |
| 8   | behavior_log    | 行为日志表 | 用户行为，用于推荐          |
| 9   | user_favorite   | 收藏表   | 用户收藏的物品            |
| 10  | recognition_log | 识别日志表 | YOLO/OCR/CLIP 调用记录 |
| 11  | system_config   | 系统配置表 | 五维权重等可配置项          |


---

## 二、表结构详述

### 2.1 user（用户表）


| 字段名           | 类型              | 必填  | 说明             |
| ------------- | --------------- | --- | -------------- |
| id            | BIGINT UNSIGNED | 是   | 主键，自增          |
| username      | VARCHAR(64)     | 是   | 用户名/昵称         |
| password_hash | VARCHAR(255)    | 是   | 密码哈希（bcrypt 等） |
| phone         | VARCHAR(20)     | 否   | 手机号，唯一         |
| student_id    | VARCHAR(32)     | 否   | 学号，唯一，可结合校园认证  |
| avatar        | VARCHAR(512)    | 否   | 头像 URL         |
| role          | TINYINT         | 是   | 1=普通用户，2=管理员   |
| status        | TINYINT         | 是   | 1=正常，0=禁用      |
| created_at    | DATETIME        | 是   | 创建时间           |
| updated_at    | DATETIME        | 是   | 更新时间           |


---

### 2.2 location（地点表）


| 字段名        | 类型              | 必填  | 说明            |
| ---------- | --------------- | --- | ------------- |
| id         | BIGINT UNSIGNED | 是   | 主键，自增         |
| name       | VARCHAR(128)    | 是   | 地点名称（如：图书馆三楼） |
| campus     | VARCHAR(64)     | 否   | 校区            |
| building   | VARCHAR(64)     | 否   | 楼栋            |
| floor      | VARCHAR(32)     | 否   | 楼层            |
| longitude  | DECIMAL(10,7)   | 否   | 经度            |
| latitude   | DECIMAL(10,7)   | 否   | 纬度            |
| created_at | DATETIME        | 是   | 创建时间          |
| updated_at | DATETIME        | 是   | 更新时间          |


---

### 2.3 item_type（物品类型表）


| 字段名        | 类型              | 必填  | 说明            |
| ---------- | --------------- | --- | ------------- |
| id         | BIGINT UNSIGNED | 是   | 主键，自增         |
| name       | VARCHAR(64)     | 是   | 类型名称（如：钥匙、钱包） |
| code       | VARCHAR(32)     | 是   | 类型编码，唯一       |
| parent_id  | BIGINT UNSIGNED | 否   | 父级 ID，0 为顶级   |
| sort       | INT             | 否   | 排序            |
| created_at | DATETIME        | 是   | 创建时间          |
| updated_at | DATETIME        | 是   | 更新时间          |


> **补充说明**：类别需与 YOLO 训练集的类别一一对应，新增类别时需同步训练数据。

---

### 2.4 item（物品表）


| 字段名             | 类型              | 必填  | 说明                    |
| --------------- | --------------- | --- | --------------------- |
| id              | BIGINT UNSIGNED | 是   | 主键，自增                 |
| user_id         | BIGINT UNSIGNED | 是   | 发布者 ID                |
| item_type       | TINYINT         | 是   | 1=寻物，2=招领             |
| item_type_id    | BIGINT UNSIGNED | 否   | 物品类型 ID（YOLO 结果）      |
| title           | VARCHAR(128)    | 是   | 标题                    |
| description     | TEXT            | 否   | 物品描述                  |
| status          | TINYINT         | 是   | 1=待认领/寻找中，2=沟通中，3=已归还 |
| location_id     | BIGINT UNSIGNED | 否   | 地点 ID                 |
| location_detail | VARCHAR(256)    | 否   | 地点补充说明                |
| lost_found_time | DATETIME        | 否   | 丢失/拾取时间               |
| contact_info    | VARCHAR(256)    | 否   | 联系方式                  |
| view_count      | INT             | 是   | 浏览次数，默认 0             |
| created_at      | DATETIME        | 是   | 创建时间                  |
| updated_at      | DATETIME        | 是   | 更新时间                  |


**状态流转**：待认领/寻找中 → 沟通中 → 已归还

---

### 2.5 item_image（物品图片表）


| 字段名          | 类型              | 必填  | 说明                 |
| ------------ | --------------- | --- | ------------------ |
| id           | BIGINT UNSIGNED | 是   | 主键，自增              |
| item_id      | BIGINT UNSIGNED | 是   | 物品 ID              |
| image_url    | VARCHAR(512)    | 是   | 图片 URL             |
| sort_order   | INT             | 是   | 排序，默认 0            |
| ocr_text     | TEXT            | 否   | OCR 提取的文本          |
| yolo_type_id | BIGINT UNSIGNED | 否   | YOLO 识别的类型 ID      |
| yolo_bbox    | JSON            | 否   | 框选坐标 [x1,y1,x2,y2] |
| created_at   | DATETIME        | 是   | 创建时间               |
| updated_at   | DATETIME        | 是   | 更新时间               |


> **补充说明**：`ocr_text` 已建全文索引，支持以文搜文的关键词检索。

---

### 2.6 item_feature（物品特征表）


| 字段名            | 类型              | 必填  | 说明            |
| -------------- | --------------- | --- | ------------- |
| id             | BIGINT UNSIGNED | 是   | 主键，自增         |
| item_id        | BIGINT UNSIGNED | 是   | 物品 ID         |
| image_id       | BIGINT UNSIGNED | 否   | 图片 ID（主图）     |
| feature_type   | TINYINT         | 是   | 1=图片向量，2=文本向量 |
| feature_vector | JSON            | 是   | 特征向量数组        |
| created_at     | DATETIME        | 是   | 创建时间          |


> **补充说明**：CLIP 向量通常 512 维，JSON 存储。大规模检索建议迁移至 Milvus、pgvector 等向量库。

---

### 2.7 message（消息表）


| 字段名          | 类型              | 必填  | 说明        |
| ------------ | --------------- | --- | --------- |
| id           | BIGINT UNSIGNED | 是   | 主键，自增     |
| from_user_id | BIGINT UNSIGNED | 是   | 发送者 ID    |
| to_user_id   | BIGINT UNSIGNED | 是   | 接收者 ID    |
| item_id      | BIGINT UNSIGNED | 是   | 关联物品 ID   |
| content      | TEXT            | 是   | 消息内容      |
| is_read      | TINYINT         | 是   | 0=未读，1=已读 |
| created_at   | DATETIME        | 是   | 创建时间      |


---

### 2.8 behavior_log（行为日志表）


| 字段名           | 类型              | 必填  | 说明                                 |
| ------------- | --------------- | --- | ---------------------------------- |
| id            | BIGINT UNSIGNED | 是   | 主键，自增                              |
| user_id       | BIGINT UNSIGNED | 否   | 用户 ID（未登录可为空）                      |
| item_id       | BIGINT UNSIGNED | 是   | 物品 ID                              |
| behavior_type | VARCHAR(32)     | 是   | view/click_contact/favorite/search |
| extra         | JSON            | 否   | 扩展信息（如搜索关键词）                       |
| created_at    | DATETIME        | 是   | 创建时间                               |


**行为类型说明**：用于协同过滤推荐，权重可配置（如点击联系 > 收藏 > 浏览）。

---

### 2.9 user_favorite（收藏表）


| 字段名        | 类型              | 必填  | 说明    |
| ---------- | --------------- | --- | ----- |
| id         | BIGINT UNSIGNED | 是   | 主键，自增 |
| user_id    | BIGINT UNSIGNED | 是   | 用户 ID |
| item_id    | BIGINT UNSIGNED | 是   | 物品 ID |
| created_at | DATETIME        | 是   | 创建时间  |


唯一约束：`(user_id, item_id)`

---

### 2.10 recognition_log（识别日志表）


| 字段名         | 类型              | 必填  | 说明            |
| ----------- | --------------- | --- | ------------- |
| id          | BIGINT UNSIGNED | 是   | 主键，自增         |
| item_id     | BIGINT UNSIGNED | 否   | 物品 ID         |
| image_id    | BIGINT UNSIGNED | 否   | 图片 ID         |
| model_type  | VARCHAR(32)     | 是   | yolo/ocr/clip |
| input_info  | JSON            | 否   | 输入信息          |
| output_info | JSON            | 否   | 输出结果          |
| cost_ms     | INT             | 否   | 耗时（毫秒）        |
| created_at  | DATETIME        | 是   | 创建时间          |


> **补充说明**：可用于监控识别效果、排查问题、优化模型。

---

### 2.11 system_config（系统配置表）


| 字段名          | 类型              | 必填  | 说明    |
| ------------ | --------------- | --- | ----- |
| id           | BIGINT UNSIGNED | 是   | 主键，自增 |
| config_key   | VARCHAR(64)     | 是   | 配置键   |
| config_value | VARCHAR(512)    | 是   | 配置值   |
| description  | VARCHAR(256)    | 否   | 说明    |
| created_at   | DATETIME        | 是   | 创建时间  |
| updated_at   | DATETIME        | 是   | 更新时间  |


**预置配置**（来源：PPT 五维权重）：


| config_key      | 默认值 | 说明       |
| --------------- | --- | -------- |
| weight_image    | 0.4 | 图像相似度权重  |
| weight_text     | 0.3 | 文本相似度权重  |
| weight_location | 0.2 | 地点距离权重   |
| weight_time     | 0.1 | 时间差权重    |
| recommend_top_n | 10  | 相关推荐返回数量 |


---

## 三、ER 关系简图

```
user ──┬──< item ──< item_image
       │      │          │
       │      │          └── item_feature
       │      │
       │      ├──< message
       │      └──< behavior_log
       │
       └──< user_favorite >── item

location >── item─ ite
item_type >─m
item_type >── item_image (yolo_type_id)
```

---

## 四、索引说明


| 表            | 索引                                                | 用途         |
| ------------ | ------------------------------------------------- | ---------- |
| item         | idx_item_type, idx_status, idx_location, idx_time | 列表筛选、搜索    |
| item_image   | ft_ocr_text                                       | 全文检索（以文搜文） |
| behavior_log | idx_user, idx_item, idx_behavior, idx_created     | 协同过滤、统计    |
| message      | idx_to_user, idx_item                             | 消息列表查询     |


---

## 五、使用说明

1. **首次部署**：执行 `schema.sql` 完成建表与基础数据初始化。
2. **类别扩展**：在 `item_type` 中新增记录，并确保与 YOLO 训练集一致。
3. **权重调优**：修改 `system_config` 中的五维权重，无需改代码。
4. **向量检索**：初期可用 JSON 存储 + 应用层计算相似度；数据量大时建议接入向量库。

