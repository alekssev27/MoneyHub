[app]
title = MoneyHub
package.name = moneyhub
package.domain = org.moneyhub

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.0
requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.2.0,pillow
orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 34
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True


[buildozer]
log_level = 2


