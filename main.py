"""
CalorieAI V5 FINAL - 全方位身材管理APP
离线AI健康管理，拍照识别食物，自动计算卡路里
"""
import os
import sys

# ===== Android路径修复 =====
if getattr(sys, 'android', False'):
    # Android环境：使用app私有目录
    APP_DIR = os.path.join(os.environ.get('ANDROID_APP_PATH', ''), 'app')
    os.chdir(APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp
from datetime import datetime
import json

from core.db import init_db, DB
from core.camera import take_photo
from core.activity import calc_total_consume, SPORT_MET, get_bmr
from ai.detector import FoodDetector
from ai.nutrition import NutritionEngine

# 加载KV
KV_PATH = os.path.join(APP_DIR, 'ui.kv')
if os.path.exists(KV_PATH):
    Builder.load_file(KV_PATH)

TODAY = datetime.now().strftime("%Y-%m-%d")


class Tab(BoxLayout, MDTabsBase):
    """Tab基类"""
    pass


class MainScreen(MDScreen):
    """主界面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai = None
        self.nutrition = None
        try:
            self.ai = FoodDetector()
            self.nutrition = NutritionEngine()
        except Exception as e:
            print(f"[AI模块初始化警告] {e}")
            self.ai = None
            self.nutrition = None

    def on_enter(self, *args):
        """进入页面时刷新"""
        self.refresh_today()

    def capture(self, meal):
        """拍照识别"""
        if self.ai is None:
            self.show_snackbar("AI模块未就绪，请检查模型文件")
            return
        take_photo(meal, lambda img: self.after_photo(img, meal))

    def after_photo(self, img_path, meal):
        """AI处理识别结果"""
        try:
            foods = self.ai.detect(img_path)
            result = self.nutrition.calculate(foods)
            DB.save_food(TODAY, meal, img_path, foods, result)
            self.refresh_today()
        except Exception as e:
            print(f"[识别失败] {e}")
            self.show_snackbar(f"识别失败: {e}")

    def manual_add_food(self):
        """手动添加食物"""
        try:
            name = self.ids.food_name.text.strip()
            kcal = float(self.ids.food_kcal.text or 0)
            protein = float(self.ids.food_protein.text or 0)
            fat = float(self.ids.food_fat.text or 0)
            meal = self.ids.meal_type.text.strip() or "零食"

            if not name:
                self.show_snackbar("请输入食物名称")
                return

            foods = [{"name": name, "conf": 1.0}]
            result = {"kcal": kcal, "protein": protein, "fat": fat}
            DB.save_food(TODAY, meal, "", foods, result)
            self.refresh_today()
            self.show_snackbar(f"已添加: {name} ({kcal}kcal)")
        except Exception as e:
            self.show_snackbar(f"添加失败: {e}")

    def calc_activity(self):
        """计算运动消耗"""
        try:
            steps = int(self.ids.steps_input.text or 0)
            sport = self.ids.sport_input.text.strip() or "其他"
            minutes = int(self.ids.minutes_input.text or 0)
            bmr = get_bmr()

            total = calc_total_consume(steps, sport, minutes, bmr)
            DB.save_activity(TODAY, steps, sport, minutes, total)
            self.refresh_today()
            self.show_snackbar(f"运动消耗: {total:.0f} kcal")
        except Exception as e:
            self.show_snackbar(f"计算失败: {e}")

    def save_body(self):
        """保存身体维度"""
        try:
            data = {
                "weight": float(self.ids.body_weight.text or 0),
                "neck": float(self.ids.body_neck.text or 0),
                "chest": float(self.ids.body_chest.text or 0),
                "waist": float(self.ids.body_waist.text or 0),
                "hip": float(self.ids.body_hip.text or 0),
                "arm": float(self.ids.body_arm.text or 0),
                "thigh": float(self.ids.body_thigh.text or 0),
            }
            DB.save_body(TODAY, data)
            self.refresh_today()
            self.show_snackbar("身体数据已保存")
        except Exception as e:
            self.show_snackbar(f"保存失败: {e}")

    def refresh_today(self):
        """刷新今日数据"""
        try:
            intake = DB.get_intake(TODAY)
            consume = DB.get_consume(TODAY)
            gap = consume - intake

            if hasattr(self.ids, 'intake_label'):
                self.ids.intake_label.text = f"🔥 摄入: {intake:.0f} kcal"
                self.ids.consume_label.text = f"🏃 消耗: {consume:.0f} kcal"
                gap_text = f"📊 缺口: {gap:+.0f} kcal"
                if gap > 0:
                    gap_text += " (减脂✅)"
                elif gap < 0:
                    gap_text += " (增重⚠️)"
                else:
                    gap_text += " (持平)"
                self.ids.gap_label.text = gap_text

            # 刷新食物记录列表
            if hasattr(self.ids, 'food_list'):
                self.ids.food_list.clear_widgets()
                records = DB.get_food_records(TODAY)
                for r in records:
                    lbl = MDLabel(
                        text=f"[{r['meal']}] {r['foods']} | {r['kcal']:.0f}kcal",
                        size_hint_y=None,
                        height=dp(30),
                        font_style="Body2"
                    )
                    self.ids.food_list.add_widget(lbl)
        except Exception as e:
            print(f"[刷新失败] {e}")

    def show_snackbar(self, text):
        """显示提示"""
        try:
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            MDSnackbar(
                MDSnackbarText(text=text),
                duration=2
            ).open()
        except:
            print(f"[提示] {text}")


class HistoryScreen(MDScreen):
    """历史记录页面"""

    def on_enter(self, *args):
        self.load_history()

    def load_history(self):
        """加载历史数据"""
        if not hasattr(self.ids, 'history_list'):
            return
        self.ids.history_list.clear_widgets()
        records = DB.get_body_history(30)
        for r in records:
            lbl = MDLabel(
                text=f"{r['date']} | 体重:{r['weight']}kg | 腰围:{r['waist']}cm",
                size_hint_y=None,
                height=dp(30),
                font_style="Body2"
            )
            self.ids.history_list.add_widget(lbl)


class ProfileScreen(MDScreen):
    """个人资料页面"""

    def on_enter(self, *args):
        info = DB.get_user_info()
        if info and hasattr(self, 'ids'):
            if hasattr(self.ids, 'gender_input'):
                self.ids.gender_input.text = info.get('gender', '男')
                self.ids.age_input.text = str(info.get('age', ''))
                self.ids.height_input.text = str(info.get('height', ''))
                self.ids.weight_input.text = str(info.get('weight', ''))

    def save_profile(self):
        """保存个人资料"""
        try:
            gender = self.ids.gender_input.text.strip() or "男"
            age = int(self.ids.age_input.text or 0)
            height = float(self.ids.height_input.text or 0)
            weight = float(self.ids.weight_input.text or 0)

            # 计算BMR
            bmr = get_bmr(gender=gender, age=age, height=height, weight=weight)
            DB.save_user_info(gender, age, height, weight, bmr)
            self.show_snackbar(f"已保存! BMR={bmr:.0f} kcal")
        except Exception as e:
            self.show_snackbar(f"保存失败: {e}")

    def show_snackbar(self, text):
        try:
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            MDSnackbar(
                MDSnackbarText(text=text),
                duration=2
            ).open()
        except:
            print(f"[提示] {text}")


class CalorieApp(MDApp):
    """主应用"""

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.theme_style = "Dark"

        init_db()

        sm = MDScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(ProfileScreen(name="profile"))
        return sm

    def switch_screen(self, screen_name):
        self.root.current = screen_name


if __name__ == "__main__":
    CalorieApp().run()
