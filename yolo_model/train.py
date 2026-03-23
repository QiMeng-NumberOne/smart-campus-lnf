from ultralytics import YOLO

# ⚠️ Windows 系统下训练，必须加上这句 if __name__ == '__main__'，否则会无限报错重启！
if __name__ == '__main__':
    
    # 1. 加载预训练模型（就像给婴儿装上一个懂基础视觉的大脑）
    # 这里我们选用最新的 YOLO11 极小杯 (Nano) 版本，速度快，适合轻薄本或初次跑通流程
    model = YOLO('yolo11n.pt') 

    print("🔥 炼丹炉已点火！正在启动训练...")

    # 2. 正式开始训练
    results = model.train(
        data='data.yaml',          # 我们的核心密码本
        epochs=50,                 # 训练轮数（先跑 50 轮试试水，完整训练一般推荐 100-300）
        imgsz=640,                 # 图像统一缩放尺寸（640 是经典黄金比例）
        batch=16,                  # 每次喂给显卡几张图（如果报错显存不足 CUDA Out of Memory，改成 8 或 4）
        name='campus_lost_v1',     # 给这次训练结果新建一个专属文件夹名字
        plots=True                 # 训练结束后自动生成各种漂亮的评估图表（给老师汇报神器）
    )

    print("🎉 恭喜！本轮炼丹圆满结束！")





