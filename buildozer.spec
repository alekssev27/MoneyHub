[app]

# Название приложения (видно на телефоне)
title = MoneyHub

# Имя пакета (только латиница, без пробелов)
package.name = moneyhub

# Домен (в обратном порядке, можно любой)
package.domain = org.alekssev27

# Папка с исходниками (где лежит main.py)
source.dir = .

# Какие файлы включать в сборку
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# Версия приложения
version = 1.0

# Зависимости (БЕЗ materialyoucolor — он не нужен для KivyMD 1.2.0)
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow

# Ориентация экрана: portrait (вертикально) / landscape / all
orientation = portrait

# Полноэкранный режим (0 = есть строка статуса, 1 = на весь экран)
fullscreen = 0

# Иконка приложения (раскомментируйте, если есть файл)
# icon.filename = %(source.dir)s/icon.png

# Заставка при запуске (раскомментируйте, если есть)
# presplash.filename = %(source.dir)s/presplash.png


[buildozer]

# Уровень логов (2 = максимально подробно, нужно для отладки)
log_level = 2

# Предупреждать при запуске от root (0 = не предупреждать, для CI)
warn_on_root = 0


# =========================================================
#                  ANDROID НАСТРОЙКИ
# =========================================================

# Целевая версия Android API
android.api = 34

# Минимальная версия Android (23 = Android 6.0)
android.minapi = 23

# Версия NDK (стабильная, совместимая с Python 3.11)
android.ndk = 25b

# Архитектуры процессоров (arm64-v8a — современные телефоны)
android.archs = arm64-v8a

# Разрешения приложения (раскомментируйте нужные)
# android.permissions = INTERNET
android.build_tools = 34.0.0
# Принять лицензии SDK автоматически (для CI обязательно)
android.accept_sdk_license = True

# Зафиксированная стабильная версия python-for-android
# (тянет Python 3.11, а не бета-3.14)
p4a.branch = 2024.01.21

# Тип сборки: debug (для теста) / release (для публикации)
# Оставляем пустым — управляется командой в main.yml

