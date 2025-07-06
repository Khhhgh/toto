# spam.py
from telegram import Update, Message
from telegram.ext import ContextTypes
import re

# كلمات ممنوعة (سب، شتائم، كلمات سيئة...)
BAD_WORDS = ["كلب", "حيوان", "ابن", "تافه", "حقير", "وسخ"]

# فلترة التكرار العشوائي (رسائل مكررة بنفس الثانية)
user_messages = {}

# دالة التحقق من الرسائل المسيئة
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    if not message or not message.text:
        return

    text = message.text.lower()
    for word in BAD_WORDS:
        if word in text:
            try:
                await message.delete()
                await context.bot.send_message(chat_id=message.chat.id, text=f"🚫 تم حذف رسالة تحتوي على كلمات مسيئة.")
            except:
                pass
            return

# دالة التحقق من الروابط
async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    if not message or not message.text:
        return

    if "http://" in message.text or "https://" in message.text or "t.me/" in message.text:
        try:
            await message.delete()
            await context.bot.send_message(chat_id=message.chat.id, text="⚠️ يمنع نشر الروابط هنا.")
        except:
            pass

# دالة التحقق من التكرار (Spam)
async def filter_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    if not message or not message.text:
        return

    user_id = message.from_user.id
    current_time = message.date.timestamp()

    if user_id in user_messages:
        last_time = user_messages[user_id]
        if current_time - last_time < 1:  # أقل من ثانية
            try:
                await message.delete()
                await context.bot.send_message(chat_id=message.chat.id, text="🚫 الرجاء عدم التكرار بسرعة.")
            except:
                pass
            return
    user_messages[user_id] = current_time

# دالة الفلترة الشاملة تستدعى من main.py
async def spam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await filter_bad_words(update, context)
    await filter_links(update, context)
    await filter_spam(update, context)
