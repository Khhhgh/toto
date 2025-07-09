import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# إعدادات السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# إعدادات Selenium لـ Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')  # تشغيل المتصفح بدون واجهة
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# دالة لتحميل الفيديو من موقع SaveFrom.net
def get_video_url(url):
    driver = None
    try:
        # تحميل أحدث إصدار من chromedriver
        driver_path = ChromeDriverManager().install()

        driver = webdriver.Chrome(service=ChromeService(driver_path), options=chrome_options)
        driver.get(f"https://ar.savefrom.net/249Ex/?url={url}")

        logger.info(f"فتح الرابط: {url}")
        
        time.sleep(5)  # زيادة الانتظار للتأكد من تحميل الصفحة بشكل صحيح

        # محاولة إيجاد زر التحميل
        try:
            download_button = driver.find_element(By.XPATH, '//button[@class="btn btn-success"]')
            download_button.click()

            time.sleep(2)

            # استخراج رابط الفيديو
            download_link = driver.find_element(By.XPATH, '//a[@id="downloadButton"]')
            video_url = download_link.get_attribute('href')

            logger.info(f"تم العثور على رابط الفيديو: {video_url}")
            return video_url
        except Exception as e:
            logger.error(f"فشل العثور على زر التحميل أو رابط الفيديو: {str(e)}")
            return None
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحميل الرابط: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()  # التأكد من إغلاق المتصفح بعد الاستخدام

# دالة للتعامل مع الرسائل
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if "https://" in user_message:  # التأكد من وجود رابط
        video_url = await asyncio.to_thread(get_video_url, user_message)
        if video_url:
            await update.message.reply_text(f"رابط الفيديو: {video_url}")
        else:
            await update.message.reply_text("حدث خطأ أثناء محاولة تحميل الفيديو.")
    else:
        await update.message.reply_text("الرجاء إرسال رابط الفيديو من SaveFrom.net.")

# دالة لبدء التفاعل مع البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! أرسل رابط الفيديو من SaveFrom.net لتحميله.")

# دالة لبدء البوت
def main():
    # إنشاء تطبيق البوت
    application = Application.builder().token("6477545499:AAHkCgwT5Sn1otiMst_sAOmoAp_QC1_ILzA").build()

    # إضافة معالج للأوامر
    application.add_handler(CommandHandler("start", start))

    # إضافة معالج للمحتوى النصي
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # تشغيل البوت
    application.run_polling()

if __name__ == '__main__':
    main()
