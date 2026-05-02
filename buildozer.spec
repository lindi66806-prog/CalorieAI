[app]

# 应用名称
title = CalorieAI

# 包名
package.name = calorieai
package.domain = com.ai.health

# 源码目录
source.dir = .
source.include_exts = py,kv,json,onnx,jpg,png,db

# 排除不需要的文件
source.exclude_exts = spec,txt,md

# 应用版本
version = 5.0.0

# 依赖库（Buildozer会自动编译）
requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.2.0,plyer,onnxruntime,numpy,pillow,sqlite3

# Android权限
android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

# Android架构 - 小米15 Pro是arm64
android.archs = arm64-v8a

# Android API级别
android.api = 34
android.minapi = 24
android.ndk = 25b

# 接受Android SDK许可
android.accept_sdk_license = True

# 图标（可选，默认用Kivy图标）
# icon.filename = %(source.dir)s/icon.png

# 启动画面方向
orientation = portrait

# 全屏
fullscreen = 0

# Android启动模式
android.allow_backup = True

# 服务
services =

# logcat级别
android.logcat_filters = *:S python:D

# p4a分支（推荐稳定版）
p4a.branch = master

# WebView（不需要）
android.allow_webview = False

[buildozer]

# 构建日志级别 (0=error, 1=info, 2=debug)
log_level = 2

# 构建警告视为错误
warn_on_root = 1
