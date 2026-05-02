"""
运动消耗计算模块
基于MET(代谢当量)标准算法
"""
from core.db import DB

# 运动MET系数表
SPORT_MET = {
    "跑步": 9.8,
    "慢跑": 7.5,
    "跳绳": 12.3,
    "快走": 4.5,
    "散步": 3.0,
    "力量训练": 6.0,
    "游泳": 8.0,
    "骑行": 7.5,
    "瑜伽": 3.0,
    "篮球": 8.0,
    "足球": 10.0,
    "羽毛球": 5.5,
    "乒乓球": 4.0,
    "爬楼梯": 8.8,
    "跳舞": 5.5,
    "划船": 7.0,
    "其他": 5.0
}


def get_bmr(gender=None, age=None, height=None, weight=None):
    """
    计算BMR基础代谢 (Mifflin-St Jeor公式)
    男性: BMR = 10×体重 + 6.25×身高 - 5×年龄 + 5
    女性: BMR = 10×体重 + 6.25×身高 - 5×年龄 - 161
    """
    if gender is None or age is None or height is None or weight is None:
        # 从数据库读取
        info = DB.get_user_info()
        if info:
            gender = gender or info.get("gender", "男")
            age = age or info.get("age", 25)
            height = height or info.get("height", 170)
            weight = weight or info.get("weight", 65)
        else:
            gender, age, height, weight = "男", 25, 170, 65

    if gender == "女":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    return max(bmr, 800)  # 最低保证800


def calc_step_consume(steps):
    """步数消耗 = 步数 × 0.04 kcal"""
    return steps * 0.04


def calc_sport_consume(sport, minutes, weight=65):
    """
    运动消耗 = MET × 3.5 × 体重(kg) / 200 × 分钟数
    """
    met = SPORT_MET.get(sport, 5.0)
    return (met * 3.5 * weight / 200) * minutes


def calc_total_consume(steps, sport, minutes, bmr=None):
    """
    每日总消耗 = BMR + 步数消耗 + 运动消耗
    """
    if bmr is None:
        bmr = get_bmr()

    step_cal = calc_step_consume(steps)
    sport_cal = calc_sport_consume(sport, minutes)

    return bmr + step_cal + sport_cal
