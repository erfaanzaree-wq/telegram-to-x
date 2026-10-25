# 🚀 Telegram → X (Twitter) Auto Cross-Poster

سیستم خودکار انتشار پست‌های کانال تلگرام در اکانت ایکس (توییتر)

هر پستی که داخل کانال [@Erfaanzare](https://t.me/Erfaanzare) بذارید، به صورت خودکار و با همان محتوا (متن + عکس) روی اکانت [x.com/ErfaanZare](https://x.com/ErfaanZare) منتشر می‌شود.

---

## ویژگی‌ها

- ✅ پشتیبانی از **متن** و **عکس**
- ✅ حفظ کپشن عکس
- ✅ جلوگیری از پست تکراری (با ذخیره آخرین message_id)
- ✅ محدودیت ۲۸۰ کاراکتر ایکس (با کوتاه‌سازی هوشمند)
- ✅ لاگ کامل برای دیباگ
- ✅ آماده اجرا روی سرور، VPS، Railway، Render و ...

---

## پیش‌نیازها

### ۱. ربات تلگرام

1. به [@BotFather](https://t.me/BotFather) بروید و یک ربات جدید بسازید (`/newbot`)
2. توکن ربات را کپی کنید
3. ربات را به عنوان **ادمین** به کانال خود اضافه کنید (حتماً دسترسی «Post Messages» یا حداقل مشاهده پست‌ها را بدهید)
4. برای دریافت `channel_post`، ربات باید ادمین کانال باشد

### ۲. دسترسی API ایکس (توییتر)

1. به [developer.x.com](https://developer.x.com/en/portal/dashboard) بروید و یک پروژه + App بسازید
2. سطح دسترسی را روی **Read and Write** قرار دهید
3. از بخش Keys and Tokens این مقادیر را بگیرید:
   - API Key
   - API Key Secret
   - Access Token
   - Access Token Secret
   - Bearer Token (اختیاری ولی توصیه می‌شود)

> **نکته مهم:** در حال حاضر برای پست کردن با API، معمولاً نیاز به پلن Basic یا بالاتر دارید. پلن Free فقط خواندن دارد.

---

## نصب و راه‌اندازی

```bash
# کلون کردن ریپو
git clone https://github.com/erfaanzaree-wq/telegram-to-x.git
cd telegram-to-x

# ساخت محیط مجازی (پیشنهادی)
python -m venv venv
source venv/bin/activate   # ویندوز: venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# کپی فایل تنظیمات
cp .env.example .env
```

حالا فایل `.env` را باز کنید و مقادیر واقعی را جایگزین کنید:

```env
TELEGRAM_BOT_TOKEN=توکن_ربات_از_BotFather
TELEGRAM_CHANNEL_ID=@Erfaanzare

X_API_KEY=...
X_API_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
X_BEARER_TOKEN=...
```

### اجرا

```bash
python main.py
```

ربات شروع به گوش دادن می‌کند و هر پست جدید کانال را فوراً به ایکس می‌فرستد.

---

## اجرا روی سرور (۲۴ ساعته)

### روش ساده با systemd (لینوکس)

```ini
# /etc/systemd/system/tg-to-x.service
[Unit]
Description=Telegram to X Cross Poster
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/telegram-to-x
ExecStart=/path/to/telegram-to-x/venv/bin/python main.py
Restart=always
RestartSec=10
EnvironmentFile=/path/to/telegram-to-x/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now tg-to-x
```

### پلتفرم‌های رایگان/ارزان

- [Railway](https://railway.app)
- [Render](https://render.com)
- [Fly.io](https://fly.io)
- [DigitalOcean App Platform](https://www.digitalocean.com)

فقط ریپو را وصل کنید، متغیرهای محیطی را ست کنید و دستور `python main.py` را بزنید.

---

## نکات فنی

| مورد | توضیح |
|------|--------|
| مدیا گروپ | فعلاً فقط عکس تکی پشتیبانی می‌شود. برای آلبوم باید توسعه داده شود |
| ویدیو | کد آماده گسترش دارد، فعلاً کامنت شده |
| لینک‌ها و منشن‌ها | به صورت متن عادی منتقل می‌شوند |
| ریپلای و فوروارد | فقط پست‌های اصلی کانال |

---

## توسعه بیشتر (ایده‌ها)

- پشتیبانی کامل از Media Group (آلبوم)
- پشتیبانی از ویدیو و گیف
- ارسال به صورت Thread اگر متن طولانی بود
- وب‌هوک به جای long polling برای عملکرد بهتر
- داشبورد ساده برای مانیتورینگ

اگر خواستی این قابلیت‌ها اضافه بشه، بگو تا توسعه بدم.

---

**ساخته شده برای:** [@Erfaanzare](https://t.me/Erfaanzare) → [@ErfaanZare](https://x.com/ErfaanZare)
