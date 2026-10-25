#!/usr/bin/env python3
"""
Telegram Channel → X (Twitter) Auto Cross-Poster
سیستم خودکار کراس‌پست از کانال تلگرام به اکانت ایکس
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telegram import Update, Message
from telegram.ext import Application, ContextTypes, MessageHandler, filters
import tweepy

load_dotenv()

# ==================== تنظیمات ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # مثلاً @Erfaanzare یا -100xxxxxxxxxx

X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")  # اختیاری

# فایل برای ذخیره آخرین پیام پردازش‌شده (جلوگیری از پست تکراری)
STATE_FILE = Path("last_message_id.txt")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_last_message_id() -> Optional[int]:
    if STATE_FILE.exists():
        try:
            return int(STATE_FILE.read_text().strip())
        except ValueError:
            return None
    return None


def save_last_message_id(message_id: int) -> None:
    STATE_FILE.write_text(str(message_id))


def create_x_client() -> tweepy.Client:
    """ساخت کلاینت API v2 ایکس با پشتیبانی از آپلود مدیا"""
    return tweepy.Client(
        bearer_token=X_BEARER_TOKEN,
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )


def create_x_api_v1() -> tweepy.API:
    """API v1.1 برای آپلود مدیا (هنوز لازم است)"""
    auth = tweepy.OAuth1UserHandler(
        X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    )
    return tweepy.API(auth)


async def download_telegram_photo(message: Message, bot) -> Optional[str]:
    """دانلود بهترین کیفیت عکس از پیام تلگرام و برگرداندن مسیر فایل"""
    if not message.photo:
        return None

    # بزرگ‌ترین سایز
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    local_path = f"/tmp/tg_photo_{message.message_id}.jpg"
    await file.download_to_drive(local_path)
    return local_path


async def post_to_x(text: str, media_path: Optional[str] = None) -> bool:
    """ارسال پست به ایکس (متن + عکس اختیاری)"""
    try:
        client = create_x_client()
        media_ids = []

        if media_path and os.path.exists(media_path):
            api_v1 = create_x_api_v1()
            media = api_v1.media_upload(filename=media_path)
            media_ids.append(media.media_id)
            logger.info(f"مدیا آپلود شد: {media.media_id}")

        # محدودیت کاراکتر ایکس (برای اکانت‌های عادی ۲۸۰)
        if len(text) > 280:
            text = text[:277] + "..."

        response = client.create_tweet(
            text=text if text.strip() else None,
            media_ids=media_ids if media_ids else None,
        )
        logger.info(f"پست موفق در ایکس: {response.data['id']}")
        return True

    except Exception as e:
        logger.error(f"خطا در ارسال به ایکس: {e}")
        return False
    finally:
        if media_path and os.path.exists(media_path):
            try:
                os.remove(media_path)
            except OSError:
                pass


async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """هندلر اصلی پست‌های کانال"""
    message = update.channel_post
    if not message:
        return

    # فیلتر کانال (اگر CHANNEL_ID تنظیم شده باشد)
    if TELEGRAM_CHANNEL_ID:
        chat_id = str(message.chat.id)
        chat_username = f"@{message.chat.username}" if message.chat.username else None
        allowed = (
            chat_id == TELEGRAM_CHANNEL_ID
            or (chat_username and chat_username.lower() == TELEGRAM_CHANNEL_ID.lower())
            or str(message.chat.id) == TELEGRAM_CHANNEL_ID.replace("@", "")
        )
        if not allowed:
            logger.debug(f"پیام از کانال دیگر نادیده گرفته شد: {message.chat.id}")
            return

    last_id = get_last_message_id()
    if last_id and message.message_id <= last_id:
        logger.info(f"پیام تکراری نادیده گرفته شد: {message.message_id}")
        return

    text = message.text or message.caption or ""
    media_path = None

    # پشتیبانی از عکس
    if message.photo:
        media_path = await download_telegram_photo(message, context.bot)
        logger.info(f"عکس دانلود شد: {media_path}")

    # پشتیبانی از ویدیو (اختیاری - می‌توانید فعال کنید)
    # if message.video:
    #     ... دانلود ویدیو و آپلود به ایکس (نیاز به تنظیمات بیشتر)

    success = await post_to_x(text, media_path)

    if success:
        save_last_message_id(message.message_id)
        logger.info(f"پست کانال {message.message_id} با موفقیت به ایکس ارسال شد")
    else:
        logger.warning(f"ارسال پست {message.message_id} ناموفق بود")


async def main() -> None:
    if not all([TELEGRAM_BOT_TOKEN, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        logger.error("متغیرهای محیطی ضروری تنظیم نشده‌اند! فایل .env را چک کنید.")
        return

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # فقط پست‌های کانال
    application.add_handler(
        MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post)
    )

    logger.info("ربات شروع به کار کرد... منتظر پست‌های کانال هستم")
    await application.run_polling(allowed_updates=["channel_post"])


if __name__ == "__main__":
    asyncio.run(main())
