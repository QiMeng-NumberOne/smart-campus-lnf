# AI 推理契约（YOLO 手动触发）

## 1) 主后端 -> 推理服务

- `POST /infer`
- 请求体：

```json
{
  "image_url": "http://127.0.0.1:8090/uploads/xxx.jpg",
  "conf_threshold": 0.5
}
```

- 返回体：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "item_class": "keys",
    "confidence": 0.91,
    "bbox": [13, 22, 150, 198]
  }
}
```

## 2) 小程序 -> 主后端（发布页手动触发）

- `POST /api/v1/ai/recognize/image`
- 请求体：

```json
{
  "image_url": "http://127.0.0.1:8090/uploads/xxx.jpg",
  "conf_threshold": 0.5
}
```

- 返回体：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "item_class": "keys",
    "confidence": 0.91,
    "bbox": [13, 22, 150, 198],
    "item_type_id": 1,
    "item_type_name": "钥匙",
    "model_version": "campus_yolo_v1",
    "source": "local"
  }
}
```

## 3) 小程序 -> 主后端（详情页手动触发，可选）

- `POST /api/v1/ai/recognize/item/{item_id}`
- 请求体：

```json
{
  "image_id": 123,
  "conf_threshold": 0.5
}
```

- 返回体：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "item_id": 12,
    "image_id": 123,
    "item_class": "keys",
    "confidence": 0.91,
    "bbox": [13, 22, 150, 198],
    "item_type_id": 1,
    "item_type_name": "钥匙",
    "model_version": "campus_yolo_v1",
    "source": "remote"
  }
}
```

## 4) 小程序 -> 主后端（采用建议）

- `POST /api/v1/ai/apply-suggestion`
- 请求体：

```json
{
  "item_id": 12,
  "image_id": 123,
  "item_type_id": 1
}
```

- 返回体：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "item_id": 12,
    "item_type_id": 1,
    "item_type_name": "钥匙"
  }
}
```
