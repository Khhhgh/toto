import logging
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os

# إعدادات التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# توكن البوت
TOKEN = "6477545499:AAHkCgwT5Sn1otiMst_sAOmoAp_QC1_ILzA"

# إعدادات السيلينيوم
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # تشغيل المتصفح بدون واجهة
options.add_argument('--no-sandbox')  # إلغاء استخدام الواجهة
options.add_argument('--disable-dev-shm-usage')  # لتجنب مشاكل الذاكرة في السحابة

# دالة لتحميل الفيديو من موقع SaveFrom.net
def get_video_url(url):
    # إعداد السيلينيوم لفتح الموقع
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://ar.savefrom.net/249Ex/?url={url}")

    try:
        # انتظار ظهور زر التحميل
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="btn btn-success"]'))
        )
        download_button.click()

        # انتظار ظهور الرابط المباشر للفيديو
        download_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@id="downloadButton"]'))
        )
        video_url = download_link.get_attribute('href')

        driver.quit()
        return video_url
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحميل الرابط: {str(e)}")
        driver.quit()
        return None

# دالة لبدء التفاعل مع البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 مرحبًا! أنا بوت لتحميل الفيديوهات 🎥\n\n"
        "أرسل لي رابط الفيديو من المواقع المدعومة مثل يوتيوب أو فيسبوك، وسأقوم بتحميله لك!"
    )

    keyboard = [
        [InlineKeyboardButton("تواصل مع المطور 📨", url="https://t.me/T_4IJ")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# دالة لتحميل الفيديو بناءً على الرابط
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        await update.message.reply_text("⚠️ الرجاء إرسال رابط صالح!")
        return

    # الحصول على رابط الفيديو المباشر باستخدام Selenium
    video_url = get_video_url(url)

    if video_url:
        await update.message.reply_text(f"✅ تم العثور على الرابط المباشر للفيديو: {video_url}")
        await update.message.reply_text(f"📥 جاري تنزيل الفيديو...")

        # تنزيل الفيديو عبر الرابط المباشر (يمكنك استخدام requests أو مكتبة أخرى لذلك)
        try:
            video_file = requests.get(video_url)
            with open("/tmp/video.mp4", 'wb') as file:
                file.write(video_file.content)
            
            # إرسال الفيديو للمستخدم
            with open("/tmp/video.mp4", 'rb') as video:
                await update.message.reply_video(video)

            # حذف الملف بعد الإرسال
            os.remove("/tmp/video.mp4")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ أثناء تنزيل الفيديو: {str(e)}")
    else:
        await update.message.reply_text("❌ حدث خطأ أثناء الحصول على رابط الفيديو.")

# إعداد البوت
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
