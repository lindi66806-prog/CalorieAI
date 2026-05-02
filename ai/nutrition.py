"""
营养计算引擎
基于本地营养数据库计算食物热量、蛋白质、脂肪
"""
import json
import os
import sys


class NutritionEngine:
    """营养计算引擎"""

    def __init__(self):
        if getattr(sys, 'android', False):
            from android.storage import app_storage_path
            db_path = os.path.join(app_storage_path(), 'assets', 'nutrition_db.json')
        else:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'assets', 'nutrition_db.json'
            )

        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
        except FileNotFoundError:
            print(f"[营养] 数据库文件不存在: {db_path}，使用内置默认值")
            self.db = self._default_db()

    def calculate(self, foods):
        """
        计算食物总营养
        foods: [{"name": "米饭", "conf": 0.9}, ...]
        返回: {"kcal": 总热量, "protein": 总蛋白质, "fat": 总脂肪}
        """
        kcal = 0.0
        protein = 0.0
        fat = 0.0

        for food in foods:
            name = food.get("name", "")
            info = self.db.get(name, self.db.get("default", {"kcal": 150, "protein": 6, "fat": 5}))
            kcal += info.get("kcal", 150)
            protein += info.get("protein", 6)
            fat += info.get("fat", 5)

        return {
            "kcal": round(kcal, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1)
        }

    def get_info(self, food_name):
        """获取单个食物营养信息"""
        return self.db.get(food_name, self.db.get("default", {"kcal": 150, "protein": 6, "fat": 5}))

    @staticmethod
    def _default_db():
        """内置默认营养数据库"""
        return {
            "default": {"kcal": 150, "protein": 6, "fat": 5},
            "米饭": {"kcal": 116, "protein": 2.6, "fat": 0.3},
            "面条": {"kcal": 137, "protein": 4.5, "fat": 0.6},
            "馒头": {"kcal": 221, "protein": 7.0, "fat": 1.1},
            "鸡蛋": {"kcal": 144, "protein": 13.3, "fat": 8.8},
            "牛奶": {"kcal": 54, "protein": 3.0, "fat": 3.2},
            "鸡肉": {"kcal": 167, "protein": 19.3, "fat": 9.4},
            "牛肉": {"kcal": 125, "protein": 19.9, "fat": 4.2},
            "猪肉": {"kcal": 143, "protein": 20.3, "fat": 6.2},
            "鱼肉": {"kcal": 104, "protein": 17.6, "fat": 3.5},
        }
