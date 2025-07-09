import logging
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def download_and_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if "http" in user_message:
        await update.message.reply_text("⏳ جاري تحميل الفيديو...")
        try:
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(None, download_video, user_message)
            
            if file_path:
                await update.message.reply_video(video=open(file_path, 'rb'))
                os.remove(file_path)  # حذف الملف بعد الإرسال
            else:
                await update.message.reply_text("❌ لم أتمكن من تحميل الفيديو.")
        except Exception as e:
            logger.error(f"خطأ أثناء تحميل أو إرسال الفيديو: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء معالجة الفيديو.")
    else:
        await update.message.reply_text("📥 الرجاء إرسال رابط فيديو صالح.")

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            # نبحث عن الملف الذي تم تنزيله
            for file in os.listdir('.'):
                if file.startswith('video.') and file.endswith(('.mp4', '.mkv', '.webm', '.mov')):
                    return file
        return None
    except Exception as e:
        logger.error(f"خطأ في تحميل الفيديو: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً! أرسل رابط الفيديو ليتم تحميله وإرساله مباشرة.")

def main():
    application = Application.builder().token("6477545499:AAHkCgwT5Sn1otiMst_sAOmoAp_QC1_ILzA").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send_video))

    application.run_polling(timeout=30)

if __name__ == "__main__":
    main()
