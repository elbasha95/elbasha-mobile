[app]

# اسم التطبيق
title = ELBASHA Downloader

# اسم الحزمة
package.name = elbashadownloader

# اسم المجلد
package.domain = com.elbasha

# المصدر الرئيسي
source.dir = .

# الملف الرئيسي
source.include_exts = py,png,jpg,kv,atlas

# الإصدار
version = 1.0

# المتطلبات - المكتبات المطلوبة
requirements = python3,kivy,yt-dlp,requests,urllib3,certifi

# الأيقونة (اختياري)
#icon.filename = %(source.dir)s/icon.png

# الصلاحيات المطلوبة
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# التوجيه
orientation = portrait

# الخدمات الخلفية
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# إصدار Android SDK
android.api = 31
android.minapi = 21
android.ndk = 25b

# التكامل مع متجر Play
android.accept_sdk_license = True

# تمكين AndroidX
android.enable_androidx = True

# معمارية المعالج
android.archs = arm64-v8a,armeabi-v7a

# السماح بالنسخ الاحتياطي
android.allow_backup = True

# وضع الملء الشاشة
fullscreen = 0

[buildozer]

# مستوى السجل (0-2)
log_level = 2

# تحذيرات
warn_on_root = 1
