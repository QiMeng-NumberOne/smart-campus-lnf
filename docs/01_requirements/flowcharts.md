# 智能校园失物招领系统 - 流程图与用户旅程

> **版本**：v1.0  
> **更新日期**：2025-03-22  
> 本文档使用 Mermaid 语法，可在 VS Code（安装 Mermaid 插件）、GitHub、GitLab 或 [Mermaid Live](https://mermaid.live/) 中渲染

---

## 一、核心业务流程图

### 1.1 失物/招领发布流程

```mermaid
flowchart TD
    A[用户选择发布类型] --> B{发布类型}
    B -->|寻物| C1[失主发布寻物]
    B -->|招领| C2[拾获者发布招领]
    C1 --> D[上传物品图片]
    C2 --> D
    D --> E[填写/补充物品信息]
    E --> F[选择地点 - LBS 打卡]
    F --> G[提交发布]
    G --> H[后端接收请求]
    H --> I[调用 YOLO 物品识别]
    I --> J[调用 OCR 文字提取]
    J --> K[融合识别结果，补全/校验信息]
    K --> L[生成 CLIP 特征向量]
    L --> M[落库并建立索引]
    M --> N[发布成功，返回结果]
```

> **补充说明**：YOLO、OCR、CLIP 的调用顺序与并联/串联策略可根据实际接口设计调整（如 OCR 与 YOLO 可并行以缩短耗时）。

### 1.2 以图搜图流程

```mermaid
flowchart TD
    A[用户上传搜索图片] --> B[后端接收]
    B --> C[YOLO 识别物品类别]
    C --> D[OCR 提取文字]
    D --> E[CLIP 生成图片特征向量]
    E --> F[向量相似度检索]
    F --> G[获取候选物品列表]
    G --> H[五维加权排序]
    H --> I[返回 Top-N 结果]
    I --> J[前端展示匹配列表]
```

### 1.3 智能推荐流程（相关失物推荐）

```mermaid
flowchart TD
    A[用户查看某条失物详情] --> B[获取当前物品 ID]
    B --> C[加载五维特征]
    C --> D[计算图像相似度 40%]
    D --> E[计算文本相似度 30%]
    E --> F[计算地点距离 20%]
    F --> G[计算时间差 10%]
    G --> H[协同过滤评分]
    H --> I[加权融合，排序]
    I --> J[返回推荐列表]
    J --> K[展示在页面底部]
```

> **补充说明**：五维权重来自 PPT。协同过滤可基于「用户浏览/收藏/联系」等行为构建，具体实现见算法设计文档。

### 1.4 认领对接流程

```mermaid
flowchart TD
    A[失主发现匹配的招领信息] --> B[点击联系拾获者]
    B --> C{联系方式展示策略}
    C -->|站内消息| D1[发送站内私信]
    C -->|脱敏展示| D2[查看脱敏手机号/微信号]
    D1 --> E[拾获者收到通知]
    D2 --> E
    E --> F[双方线下协商交接]
    F --> G[确认归还]
    G --> H[更新物品状态为 已归还]
    H --> I[可选：双方互评]
```

> **补充说明**：联系方式的展示方式（站内消息 vs 脱敏展示）需结合隐私与产品策略确定，此处列出两种常见方案。

---

## 二、系统数据流图

### 2.1 发布接口数据流

```mermaid
sequenceDiagram
    participant U as 用户/前端
    participant API as 后端 API
    participant Y as YOLO 服务
    participant O as OCR 服务
    participant C as CLIP 服务
    participant DB as 数据库

    U->>API: POST 发布（图片 + 表单）
    API->>Y: 调用物品识别
    Y-->>API: 物品类别 + 框选
    API->>O: 调用文字识别
    O-->>API: 提取文本
    API->>API: 融合识别结果
    API->>C: 生成图片向量
    C-->>API: 特征向量
    API->>DB: 写入物品表、特征表
    API-->>U: 返回发布成功
```

### 2.2 搜索接口数据流

```mermaid
sequenceDiagram
    participant U as 用户/前端
    participant API as 后端 API
    participant Y as YOLO
    participant O as OCR
    participant C as CLIP
    participant VDB as 向量库/数据库

    U->>API: POST 搜索（图片 或 文本）
    alt 以图搜图
        API->>Y: 识别
        API->>O: 提取文字
        API->>C: 生成向量
        C-->>API: 查询向量
    else 以文搜文
        API->>C: 文本编码为向量
    end
    API->>VDB: 相似度检索
    VDB-->>API: 候选列表
    API->>API: 五维加权排序
    API-->>U: 返回排序后的结果
```

> **补充说明**：向量库可采用 MySQL + 向量扩展、Milvus、Elasticsearch 等，具体选型见技术方案。

---

## 三、用户旅程 (User Journey)

### 3.1 失主寻物旅程

```mermaid
journey
    title 失主寻物旅程
    section 发现丢失
        意识到物品丢失: 2: 失主
        回忆丢失地点与时间: 3: 失主
    section 发布寻物
        打开系统: 4: 失主
        上传物品照片: 5: 失主
        填写描述与地点: 4: 失主
        提交发布: 5: 失主
    section 搜索匹配
        以图搜图/以文搜文: 5: 失主
        浏览匹配结果: 5: 失主
        查看相关推荐: 4: 失主
    section 联系归还
        联系拾获者: 5: 失主
        线下交接: 5: 失主
        确认归还并更新状态: 5: 失主
```

### 3.2 拾获者招领旅程

```mermaid
journey
    title 拾获者招领旅程
    section 捡到物品
        捡到失物: 4: 拾获者
        决定发布招领: 5: 拾获者
    section 发布招领
        拍照上传: 5: 拾获者
        填写拾取地点与时间: 5: 拾获者
        提交发布: 5: 拾获者
    section 等待认领
        收到失主咨询: 5: 拾获者
        核实信息: 4: 拾获者
    section 完成归还
        约定交接: 5: 拾获者
        归还物品: 5: 拾获者
        更新状态: 5: 拾获者
```

---

## 四、状态机

### 4.1 物品状态流转

```mermaid
stateDiagram-v2
    [*] --> 待认领: 发布招领
    [*] --> 寻找中: 发布寻物
    待认领 --> 沟通中: 失主发起联系
    寻找中 --> 沟通中: 拾获者响应
    沟通中 --> 已归还: 确认归还
    沟通中 --> 待认领: 沟通失败/取消
    沟通中 --> 寻找中: 沟通失败/取消
    已归还 --> [*]
```

> **补充说明**：状态命名可根据业务习惯调整为「待匹配」「已匹配」「已交接」等。

### 4.2 用户操作与系统响应

```mermaid
stateDiagram-v2
    [*] --> 浏览: 进入系统
    浏览 --> 搜索: 发起搜索
    浏览 --> 发布: 发起发布
    搜索 --> 查看详情: 点击某条结果
    查看详情 --> 联系: 点击联系
    联系 --> 沟通: 进入沟通
    发布 --> 浏览: 发布成功
    沟通 --> 浏览: 完成/取消
```

---

## 五、ER 关系示意（概念级）

```mermaid
erDiagram
    USER ||--o{ ITEM : 发布
    ITEM ||--o{ ITEM_IMAGE : 包含
    ITEM }o--|| ITEM_TYPE : 属于
    ITEM ||--o{ CLIP_FEATURE : 对应
    USER ||--o{ MESSAGE : 发送
    MESSAGE }o--|| ITEM : 关联
    USER ||--o{ BEHAVIOR_LOG : 产生
    BEHAVIOR_LOG }o--|| ITEM : 关联
    ITEM ||--o{ LOCATION : 有地点
```

> **补充说明**：具体表结构见 `../03_database/` 下的建表 SQL 与数据字典。

---

## 六、渲染说明

| 环境 | 说明 |
|------|------|
| VS Code | 安装 `Markdown Preview Mermaid Support` 插件后预览 |
| GitHub / GitLab | 原生支持 Mermaid 渲染 |
| 在线 | 复制到 [Mermaid Live Editor](https://mermaid.live/) 查看 |
