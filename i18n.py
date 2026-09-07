# -*- coding: utf-8 -*-
"""
pm2-app — Translations (English / العربية / Bahasa Indonesia).

Every user-visible string lives here so switching language re-labels the whole
UI. The three languages were written and reviewed individually; placeholders
like {name} must exist in every language with the same name.
"""

LANGS = ("en", "ar", "id")

LANG_NATIVE = {
    "en": "English",
    "ar": "العربية",
    "id": "Indonesia",
}

# --------------------------------------------------------------------------
# Keys -> {language: text}. Placeholders: {name}, {n}, {cmd}, {path}.
# --------------------------------------------------------------------------
STRINGS = {
    # ---------- App header ----------
    "app.tagline": {
        "en": "Run your bots in the background — no terminal needed.",
        "ar": "شغّل بوتاتك في الخلفية — دون الحاجة إلى الطرفية.",
        "id": "Jalankan bot Anda di latar belakang — tanpa perlu terminal.",
    },
    "pm2.ready": {
        "en": "PM2 ready",
        "ar": "PM2 جاهز",
        "id": "PM2 siap",
    },
    "pm2.missing": {
        "en": "PM2 is not installed",
        "ar": "PM2 غير مثبَّت",
        "id": "PM2 tidak terpasang",
    },
    "pm2.installBtn": {
        "en": "Install PM2",
        "ar": "تثبيت PM2",
        "id": "Pasang PM2",
    },
    "pm2.autoTitle": {
        "en": "Installing PM2…",
        "ar": "جارٍ تثبيت PM2…",
        "id": "Memasang PM2…",
    },
    "pm2.autoMsg": {
        "en": "PM2 was not found, so pm2-app is installing it for you now. It usually takes less than a minute — please wait.",
        "ar": "لم يتم العثور على PM2، لذلك يقوم pm2-app بتثبيته لك الآن. يستغرق ذلك أقل من دقيقة عادةً — انتظر من فضلك.",
        "id": "PM2 tidak ditemukan, jadi pm2-app sedang memasangnya untuk Anda sekarang. Biasanya kurang dari satu menit — mohon tunggu.",
    },
    "pm2.installedToast": {
        "en": "PM2 installed ✓ Now drag your bot into the box above",
        "ar": "تم تثبيت PM2 ✓ اسحب بوتك الآن إلى الصندوق بالأعلى",
        "id": "PM2 terpasang ✓ Sekarang seret bot Anda ke kotak di atas",
    },
    "err.needNode": {
        "en": "PM2 runs on Node.js, and Node.js was not found on this computer.\n\nPlease open a terminal (Ctrl+Alt+T) and install it with:\n\n    sudo apt update && sudo apt install -y nodejs npm\n\nThen open pm2-app again — it will install PM2 automatically.",
        "ar": "PM2 يعمل عبر Node.js، ولم يتم العثور على Node.js على هذا الجهاز.\n\nمن فضلك افتح الطرفية (Ctrl+Alt+T) وقم بتثبيته بالأمر التالي:\n\n    sudo apt update && sudo apt install -y nodejs npm\n\nثم افتح pm2-app مجددًا — وسيثبّت PM2 تلقائيًا.",
        "id": "PM2 berjalan di atas Node.js, dan Node.js tidak ditemukan di komputer ini.\n\nSilakan buka terminal (Ctrl+Alt+T) lalu pasang dengan perintah:\n\n    sudo apt update && sudo apt install -y nodejs npm\n\nLalu buka pm2-app lagi — PM2 akan dipasang secara otomatis.",
    },
    "err.installFailedTitle": {
        "en": "PM2 could not be installed automatically",
        "ar": "تعذّر تثبيت PM2 تلقائيًا",
        "id": "PM2 tidak dapat dipasang secara otomatis",
    },
    "btn.copyCmd": {
        "en": "Copy command",
        "ar": "نسخ الأمر",
        "id": "Salin perintah",
    },

    # ---------- Drop zone ----------
    "drop.title": {
        "en": "Drag & drop your bot here",
        "ar": "اسحب ملف بوتك وأفلته هنا",
        "id": "Seret bot Anda ke sini",
    },
    "drop.subtitle": {
        "en": "A file (.js · .py · .sh) or a folder that contains your bot",
        "ar": "أي ملف (js · py · sh) أو مجلد يحتوي على بوتك",
        "id": "File (.js · .py · .sh) atau folder berisi bot Anda",
    },
    "drop.browseFile": {
        "en": "Choose a file",
        "ar": "اختيار ملف",
        "id": "Pilih file",
    },
    "drop.browseFolder": {
        "en": "Choose a folder",
        "ar": "اختيار مجلد",
        "id": "Pilih folder",
    },

    # ---------- Pending (ready-to-start) queue ----------
    "queue.title": {
        "en": "Ready to start",
        "ar": "جاهزة للتشغيل",
        "id": "Siap dijalankan",
    },
    "queue.empty": {
        "en": "Drop a bot above and it will appear here",
        "ar": "أسقط البوت بالأعلى وسيظهر هنا",
        "id": "Seret bot di atas dan ia akan muncul di sini",
    },
    "queue.runAll": {
        "en": "Run all",
        "ar": "تشغيل الكل",
        "id": "Jalankan semua",
    },
    "queue.clear": {
        "en": "Clear",
        "ar": "مسح",
        "id": "Bersihkan",
    },
    "action.run": {
        "en": "Run",
        "ar": "تشغيل",
        "id": "Jalankan",
    },
    "action.remove": {
        "en": "Remove",
        "ar": "إزالة",
        "id": "Hapus",
    },
    "toast.started": {
        "en": "“{name}” is now running in the background ✓",
        "ar": "أصبح «{name}» يعمل الآن في الخلفية ✓",
        "id": "“{name}” kini berjalan di latar belakang ✓",
    },
    "toast.stopped": {
        "en": "“{name}” stopped",
        "ar": "تم إيقاف «{name}»",
        "id": "“{name}” dihentikan",
    },
    "toast.deleted": {
        "en": "“{name}” deleted from PM2",
        "ar": "تم حذف «{name}» من PM2",
        "id": "“{name}” dihapus dari PM2",
    },
    "toast.restarted": {
        "en": "“{name}” restarted",
        "ar": "تمت إعادة تشغيل «{name}»",
        "id": "“{name}” dimulai ulang",
    },

    # ---------- Entry types ----------
    "entry.nodeFile": {
        "en": "JavaScript / Node.js",
        "ar": "جافاسكربت / Node.js",
        "id": "JavaScript / Node.js",
    },
    "entry.nodeProject": {
        "en": "Node.js project (package.json)",
        "ar": "مشروع Node.js (package.json)",
        "id": "Proyek Node.js (package.json)",
    },
    "entry.python": {
        "en": "Python script",
        "ar": "سكربت بايثون",
        "id": "Skrip Python",
    },
    "entry.bash": {
        "en": "Bash script",
        "ar": "سكربت Bash",
        "id": "Skrip Bash",
    },
    "entry.other": {
        "en": "File",
        "ar": "ملف",
        "id": "File",
    },

    # ---------- Running apps list ----------
    "apps.title": {
        "en": "Running with PM2",
        "ar": "تعمل عبر PM2",
        "id": "Berjalan dengan PM2",
    },
    "apps.refresh": {
        "en": "Refresh",
        "ar": "تحديث",
        "id": "Segarkan",
    },
    "apps.count": {
        "en": "{n} running",
        "ar": "{n} تعمل الآن",
        "id": "{n} berjalan",
    },
    "apps.emptyTitle": {
        "en": "Nothing is running yet",
        "ar": "لا شيء يعمل بعد",
        "id": "Belum ada yang berjalan",
    },
    "apps.emptySub": {
        "en": "Drag your bot into the box above and press Run. It will keep running in the background even after you close this app.",
        "ar": "اسحب بوتك إلى الصندوق بالأعلى واضغط «تشغيل». سيستمر في العمل بالخلفية حتى بعد إغلاق هذا التطبيق.",
        "id": "Seret bot Anda ke kotak di atas lalu tekan Jalankan. Bot akan terus berjalan di latar belakang meski aplikasi ini ditutup.",
    },

    # ---------- Status ----------
    "status.online": {
        "en": "Online",
        "ar": "يعمل",
        "id": "Berjalan",
    },
    "status.stopped": {
        "en": "Stopped",
        "ar": "متوقف",
        "id": "Berhenti",
    },
    "status.stopping": {
        "en": "Stopping…",
        "ar": "جارٍ الإيقاف…",
        "id": "Menghentikan…",
    },
    "status.launching": {
        "en": "Launching…",
        "ar": "جارٍ التشغيل…",
        "id": "Memulai…",
    },
    "status.errored": {
        "en": "Error",
        "ar": "خطأ",
        "id": "Gagal",
    },
    "status.unknown": {
        "en": "Unknown",
        "ar": "غير معروف",
        "id": "Tidak diketahui",
    },

    # ---------- Process metadata ----------
    "meta.uptime": {
        "en": "Uptime",
        "ar": "مدة التشغيل",
        "id": "Waktu aktif",
    },
    "meta.restarts": {
        "en": "Restarts",
        "ar": "مرات إعادة التشغيل",
        "id": "Restart",
    },
    "meta.cpu": {
        "en": "CPU",
        "ar": "المعالج",
        "id": "CPU",
    },
    "meta.mem": {
        "en": "Memory",
        "ar": "الذاكرة",
        "id": "Memori",
    },
    "meta.path": {
        "en": "Location: {path}",
        "ar": "المسار: {path}",
        "id": "Lokasi: {path}",
    },
    "action.restart": {
        "en": "Restart",
        "ar": "إعادة تشغيل",
        "id": "Mulai ulang",
    },
    "action.stop": {
        "en": "Stop",
        "ar": "إيقاف",
        "id": "Hentikan",
    },
    "action.delete": {
        "en": "Delete",
        "ar": "حذف",
        "id": "Hapus",
    },
    "action.logs": {
        "en": "Logs",
        "ar": "السجلات",
        "id": "Log",
    },
    "action.openFolder": {
        "en": "Open folder",
        "ar": "فتح المجلد",
        "id": "Buka folder",
    },

    # ---------- Confirmation ----------
    "confirm.deleteTitle": {
        "en": "Delete app?",
        "ar": "حذف التطبيق؟",
        "id": "Hapus aplikasi?",
    },
    "confirm.deleteMsg": {
        "en": "Are you sure you want to stop and delete “{name}” from PM2?",
        "ar": "هل أنت متأكد من إيقاف «{name}» وحذفه من PM2؟",
        "id": "Yakin ingin menghentikan dan menghapus “{name}” dari PM2?",
    },
    "confirm.stopTitle": {
        "en": "Stop app?",
        "ar": "إيقاف التطبيق؟",
        "id": "Hentikan aplikasi?",
    },
    "confirm.stopMsg": {
        "en": "Do you want to stop “{name}”? It will stay in the list and can be started again.",
        "ar": "هل تريد إيقاف «{name}»؟ سيبقى في القائمة ويمكنك تشغيله مجددًا.",
        "id": "Hentikan “{name}”? Aplikasi akan tetap ada di daftar dan bisa dijalankan lagi.",
    },
    "btn.yes": {
        "en": "Yes",
        "ar": "نعم",
        "id": "Ya",
    },
    "btn.cancel": {
        "en": "Cancel",
        "ar": "إلغاء",
        "id": "Batal",
    },
    "btn.close": {
        "en": "Close",
        "ar": "إغلاق",
        "id": "Tutup",
    },
    "btn.copy": {
        "en": "Copy",
        "ar": "نسخ",
        "id": "Salin",
    },

    # ---------- Logs console ----------
    "logs.title": {
        "en": "Live logs",
        "ar": "السجلات المباشرة",
        "id": "Log langsung",
    },
    "logs.none": {
        "en": "Select an app above to watch its logs here.",
        "ar": "اختر تطبيقًا من الأعلى لعرض سجلاته هنا.",
        "id": "Pilih aplikasi di atas untuk melihat log-nya di sini.",
    },
    "logs.clear": {
        "en": "Clear",
        "ar": "مسح",
        "id": "Bersihkan",
    },
    "logs.copy": {
        "en": "Copy logs",
        "ar": "نسخ السجلات",
        "id": "Salin log",
    },
    "logs.noFile": {
        "en": "No log file for this app yet.",
        "ar": "لا يوجد ملف سجلات لهذا التطبيق بعد.",
        "id": "Belum ada file log untuk aplikasi ini.",
    },

    # ---------- Boot / auto-start ----------
    "boot.label": {
        "en": "Auto-start on boot",
        "ar": "تشغيل تلقائي عند فتح الجهاز",
        "id": "Mulai otomatis saat boot",
    },
    "boot.on": {
        "en": "On",
        "ar": "مفعّل",
        "id": "Aktif",
    },
    "boot.off": {
        "en": "Off",
        "ar": "معطّل",
        "id": "Nonaktif",
    },
    "boot.hint": {
        "en": "Make every app in the list start by itself after you restart your computer.",
        "ar": "اجعل كل البوتات في القائمة تعمل تلقائيًا بعد إعادة تشغيل جهازك.",
        "id": "Buat semua aplikasi dalam daftar berjalan sendiri setelah komputer dinyalakan ulang.",
    },
    "boot.dialogTitle": {
        "en": "Run apps automatically after a restart?",
        "ar": "تشغيل البوتات تلقائيًا بعد إعادة تشغيل الجهاز؟",
        "id": "Jalankan aplikasi otomatis setelah restart?",
    },
    "boot.dialogMsg": {
        "en": "PM2 will save the current list, then register itself with the system so every bot starts again after you restart your computer.\n\nPM2 needs your password once (sudo). The command below was copied to your clipboard — open a terminal (Ctrl+Alt+T), paste it, and press Enter:\n\n{cmd}\n\nWhen it finishes, press “Done”. The status above will turn green.",
        "ar": "سيحفظ PM2 القائمة الحالية، ثم يثبّت نفسه في النظام بحيث تُشغَّل جميع البوتات تلقائيًا بعد إعادة تشغيل جهازك.\n\nيحتاج PM2 إلى كلمة مرورك مرة واحدة (صلاحيات sudo). الأمر بالأسفل تم نسخه إلى الحافظة — افتح الطرفية (Ctrl+Alt+T) وألصقه ثم اضغط Enter:\n\n{cmd}\n\nعند انتهائه اضغط «تم» وستتحول الحالة بالأعلى إلى اللون الأخضر.",
        "id": "PM2 akan menyimpan daftar saat ini, lalu mendaftarkan dirinya ke sistem agar semua bot berjalan lagi secara otomatis setelah komputer Anda dinyalakan ulang.\n\nPM2 meminta kata sandi Anda sekali (sudo). Perintah di bawah sudah disalin ke clipboard — buka terminal (Ctrl+Alt+T), tempel, lalu tekan Enter:\n\n{cmd}\n\nSetelah selesai, tekan “Selesai”. Status di atas akan berubah hijau.",
    },
    "boot.done": {
        "en": "Done",
        "ar": "تم",
        "id": "Selesai",
    },
    "boot.later": {
        "en": "Later",
        "ar": "لاحقًا",
        "id": "Nanti",
    },
    "boot.enabledToast": {
        "en": "Auto-start enabled ✓ Bots will return after a restart",
        "ar": "تم تفعيل التشغيل التلقائي ✓ ستعود البوتات بعد إعادة التشغيل",
        "id": "Mulai otomatis aktif ✓ Bot akan berjalan lagi setelah restart",
    },
    "boot.savedToast": {
        "en": "List saved ✓ Enable auto-start above to keep bots after a restart",
        "ar": "تم حفظ القائمة ✓ فعّل «التشغيل التلقائي» بالأعلى لتستمر البوتات بعد إعادة التشغيل",
        "id": "Daftar disimpan ✓ Aktifkan “Mulai otomatis” di atas agar bot tetap berjalan setelah restart",
    },

    # ---------- Install PM2 ----------
    "install.title": {
        "en": "Install PM2",
        "ar": "تثبيت PM2",
        "id": "Pasang PM2",
    },
    "install.msg": {
        "en": "PM2 is a small tool that runs on Node.js. To install it, open a terminal (Ctrl+Alt+T) and run this command:\n\n    sudo npm install -g pm2\n\nEnter your password when asked, then come back and press “Check again”.",
        "ar": "PM2 أداة صغيرة تعمل عبر Node.js. لتثبيتها، افتح الطرفية (Ctrl+Alt+T) ونفّذ هذا الأمر:\n\n    sudo npm install -g pm2\n\nأدخل كلمة مرورك عند الطلب، ثم ارجع إلى هنا واضغط «التحقق مجددًا».",
        "id": "PM2 adalah alat kecil berbasis Node.js. Untuk memasangnya, buka terminal (Ctrl+Alt+T) lalu jalankan perintah ini:\n\n    sudo npm install -g pm2\n\nMasukkan kata sandi Anda saat diminta, lalu kembali ke sini dan tekan “Periksa lagi”.",
    },
    "install.checkAgain": {
        "en": "Check again",
        "ar": "التحقق مجددًا",
        "id": "Periksa lagi",
    },

    # ---------- Errors ----------
    "err.startFailed": {
        "en": "Could not start “{name}”",
        "ar": "تعذّر تشغيل «{name}»",
        "id": "Gagal menjalankan “{name}”",
    },
    "err.pm2": {
        "en": "PM2 returned an error",
        "ar": "حدث خطأ من PM2",
        "id": "Terjadi kesalahan pada PM2",
    },
    "err.notFound": {
        "en": "The file or folder was not found: {path}",
        "ar": "الملف أو المجلد غير موجود: {path}",
        "id": "File atau folder tidak ditemukan: {path}",
    },
    "err.unsupported": {
        "en": "This file type is not supported.\nSupported: .js, .mjs, .cjs, .py, .sh — or a folder containing package.json / index.js / main.js.",
        "ar": "نوع الملف غير مدعوم.\nالمدعوم: js · mjs · cjs · py · sh — أو مجلد يحتوي على package.json أو index.js أو main.js.",
        "id": "Jenis file ini tidak didukung.\nDidukung: .js, .mjs, .cjs, .py, .sh — atau folder berisi package.json / index.js / main.js.",
    },
    "err.noEntry": {
        "en": "No entry file found in this folder.\nPut your bot's main file here, or drop the file itself.",
        "ar": "لم يتم العثور على ملف رئيسي داخل هذا المجلد.\nضع ملف البوت الرئيسي فيه، أو أسقط الملف نفسه.",
        "id": "Tidak ada file utama di folder ini.\nLetakkan file utama bot di folder tersebut, atau seret file-nya langsung.",
    },
    "err.dropTitle": {
        "en": "Could not add some items",
        "ar": "تعذّرت إضافة بعض العناصر",
        "id": "Beberapa item tidak dapat ditambahkan",
    },
    "err.openFolder": {
        "en": "Could not open the folder in the file manager.",
        "ar": "تعذّر فتح المجلد في مدير الملفات.",
        "id": "Folder tidak bisa dibuka di pengelola file.",
    },

    # ---------- Help dialog ----------
    "help.title": {
        "en": "How it works",
        "ar": "كيف يعمل التطبيق",
        "id": "Cara kerja",
    },
    "help.p1": {
        "en": "Drag a bot file or folder into the box above.",
        "ar": "اسحب ملف البوت أو المجلد إلى الصندوق بالأعلى.",
        "id": "Seret file atau folder bot ke kotak di atas.",
    },
    "help.p2": {
        "en": "Press Run — PM2 starts it in the background for you.",
        "ar": "اضغط «تشغيل» — سيشغّله PM2 لك في الخلفية.",
        "id": "Tekan Jalankan — PM2 akan menjalankannya di latar belakang.",
    },
    "help.p3": {
        "en": "Close this app whenever you want — your bot keeps running.",
        "ar": "أغلق التطبيق متى شئت — بوتك يستمر في العمل.",
        "id": "Tutup aplikasi ini kapan pun — bot Anda tetap berjalan.",
    },
    "help.p4": {
        "en": "Tip: switch on “Auto-start on boot” so your bots come back after a PC restart.",
        "ar": "نصيحة: فعّل «التشغيل التلقائي عند فتح الجهاز» لتعود بوتاتك بعد إعادة تشغيل الجهاز.",
        "id": "Tips: aktifkan “Mulai otomatis saat boot” agar bot Anda berjalan lagi setelah PC di-restart.",
    },
    "help.link": {
        "en": "Need help? Ask here",
        "ar": "تحتاج مساعدة؟ اسأل هنا",
        "id": "Butuh bantuan? Tanyakan di sini",
    },
}


def t(lang, key, **kwargs):
    """Translate `key` into `lang`, formatting any {placeholders}."""
    entry = STRINGS.get(key)
    if not entry:
        return "??" + key
    text = entry.get(lang) or entry.get("en") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
