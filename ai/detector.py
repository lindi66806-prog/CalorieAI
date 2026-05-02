"""
AI食物识别模块 - ONNX推理版
支持YOLOv8 ONNX模型，带降级处理
"""
import os
import sys

# 模型路径
if getattr(sys, 'android', False):
    from android.storage import app_storage_path
    MODEL_DIR = os.path.join(app_storage_path(), 'ai')
else:
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(MODEL_DIR, 'yolov8_food.onnx')

# 食物类别标签（简版，可扩展）
FOOD_LABELS = [
    "米饭", "面条", "馒头", "包子", "饺子",
    "炒菜", "火锅", "烧烤", "沙拉", "三明治",
    "汉堡", "披萨", "寿司", "粥", "汤",
    "鸡蛋", "牛奶", "酸奶", "面包", "蛋糕",
    "水果", "蔬菜", "鸡肉", "牛肉", "猪肉",
    "鱼肉", "虾", "豆腐", "坚果", "薯条",
    "可乐", "奶茶", "咖啡", "果汁", "啤酒"
]


class FoodDetector:
    """食物检测器"""

    def __init__(self):
        self.session = None
        self.available = False

        if os.path.exists(MODEL_PATH):
            try:
                import onnxruntime as ort
                self.session = ort.InferenceSession(
                    MODEL_PATH,
                    providers=['CPUExecutionProvider']
                )
                self.available = True
                print(f"[AI] ONNX模型加载成功: {MODEL_PATH}")
            except Exception as e:
                print(f"[AI] ONNX加载失败: {e}")
                self.available = False
        else:
            print(f"[AI] 模型文件不存在: {MODEL_PATH}")
            print("[AI] 将使用降级模式（随机匹配营养库）")
            self.available = False

    def detect(self, img_path):
        """
        识别食物
        返回: [{"name": "食物名", "conf": 置信度}, ...]
        """
        if self.available and self.session is not None:
            return self._detect_onnx(img_path)
        else:
            return self._detect_fallback(img_path)

    def _detect_onnx(self, img_path):
        """ONNX推理"""
        try:
            import numpy as np
            from PIL import Image

            img = Image.open(img_path).convert('RGB').resize((640, 640))
            img_array = np.array(img).astype(np.float32) / 255.0
            img_array = img_array.transpose(2, 0, 1)[None, ...]

            outputs = self.session.run(None, {"images": img_array})
            preds = outputs[0][0]

            # 解析YOLOv8输出
            foods = []
            for det in preds:
                # YOLOv8输出格式: [x1, y1, x2, y2, conf, class_scores...]
                if len(det) >= 6:
                    conf = float(det[4])
                    if conf > 0.3:  # 置信度阈值
                        cls_id = int(det[5:].argmax()) if len(det) > 6 else 0
                        name = FOOD_LABELS[cls_id % len(FOOD_LABELS)]
                        foods.append({"name": name, "conf": conf})

            # 最多取前5个
            return foods[:5]

        except Exception as e:
            print(f"[AI] ONNX推理失败: {e}")
            return self._detect_fallback(img_path)

    def _detect_fallback(self, img_path):
        """
        降级模式：无法使用ONNX时
        返回默认食物，让用户手动修正
        """
        # 读取营养库中的常见食物
        try:
            import json
            nutrition_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'assets', 'nutrition_db.json'
            )
            with open(nutrition_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
            common_foods = [k for k in db.keys() if k != "default"][:3]
            return [{"name": name, "conf": 0.5} for name in common_foods]
        except:
            return [{"name": "混合食物", "conf": 0.5}]
