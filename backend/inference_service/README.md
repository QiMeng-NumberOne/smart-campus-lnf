# Inference Service

## 启动

```bash
cd backend/inference_service
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8100
```

## 接口

- `GET /health`
- `POST /infer`

请求样例：

```json
{
  "image_url": "http://127.0.0.1:8090/uploads/xxx.jpg",
  "conf_threshold": 0.5
}
```

## 主后端配置

在 `backend/.env` 配置：

```env
AI_INFER_URL=http://127.0.0.1:8100
AI_TIMEOUT_SEC=5
```
