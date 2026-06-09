[app]
title = MoneyHub
package.name = moneyhub
package.domain = org.alekssev27
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 1.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0

# ===== ANDROID =====
android.api = 34
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = 2024.01.21
