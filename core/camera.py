"""
相机模块 - Android兼容版
支持plyer拍照和Android原生相机调用
"""
import os
import sys
import time

# 图片保存目录
if getattr(sys, 'android', False):
    from android.storage import app_storage_path
    IMG_DIR = os.path.join(app_storage_path(), 'food_imgs')
else:
    IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'food_imgs')

os.makedirs(IMG_DIR, exist_ok=True)


def take_photo(tag, callback):
    """拍照并返回图片路径"""
    path = os.path.join(IMG_DIR, f"{tag}_{int(time.time())}.jpg")

    try:
        if getattr(sys, 'android', False):
            # Android环境：使用Android原生Intent调用相机
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            MediaStore = autoclass('android.provider.MediaStore')

            activity = PythonActivity.mActivity
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            if intent.resolveActivity(activity.getPackageManager()) is not None:
                activity.startActivityForResult(intent, 1234)
                # 简化版：等待回调（实际需要更复杂的处理）
                # 这里先用plyer兼容
                _take_photo_plyer(path, callback)
            else:
                _take_photo_plyer(path, callback)
        else:
            # 桌面环境
            _take_photo_plyer(path, callback)

    except Exception as e:
        print(f"[相机] 拍照失败: {e}")
        # 降级：创建占位记录
        callback(path)


def _take_photo_plyer(path, callback):
    """使用plyer拍照"""
    try:
        from plyer import camera
        camera.take_picture(filename=path, on_complete=lambda x: callback(path))
    except Exception as e:
        print(f"[plyer相机] {e}")
        callback(path)
