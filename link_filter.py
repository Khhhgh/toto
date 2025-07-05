from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

# تخزين حالة كل مجموعة: True = مفعلة، False = معطلة
links_status = {}
chat_status = {}

async def is_admin(update: Update):
    user_id = update.effective_user.id
    chat = update.effective_chat
    member = await chat.get_member(user_id)
    return member.status in ["administrator", "creator"]

# معالجة أوامر فتح/تعطيل الروابط وفتح/غلق الدردشة
async def link_chat_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if not await is_admin(update):
        return  # فقط المشرفين والمالك

    # إعداد الحالة الافتراضية لو لم تكن موجودة
    if chat_id not in links_status:
        links_status[chat_id] = True  # روابط مفعلة
    if chat_id not in chat_status:
        chat_status[chat_id] = True  # دردشة مفتوحة

    # أوامر التحكم
    if text == "فتح الروابط":
        links_status[chat_id] = True
        await update.message.reply_text("✅ تم تفعيل الروابط في هذه المجموعة.")
    elif text == "تعطيل الروابط":
        links_status[chat_id] = False
        await update.message.reply_text("❌ تم تعطيل الروابط في هذه المجموعة.")
    elif text == "فتح الدردشة":
        chat_status[chat_id] = True
        await update.message.reply_text("✅ تم فتح الدردشة لجميع الأعضاء.")
    elif text == "غلق الدردشة":
        chat_status[chat_id] = False
        await update.message.reply_text("❌ تم غلق الدردشة، فقط المشرفين يمكنهم الكتابة.")

# فلتر حذف الروابط وتعطيل إرسال الرسائل عند غلق الدردشة
async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    text = update.message.text or ""

    # افتراض حالة تفعيل لو لا موجودة
    links_enabled = links_status.get(chat_id, True)
    chat_open = chat_status.get(chat_id, True)

    # إذا الدردشة مغلقة والمستخدم ليس مشرف أو مالك => حذف الرسالة
    member = await update.effective_chat.get_member(user_id)
    if not chat_open and member.status not in ["administrator", "creator"]:
        await update.message.delete()
        return

    # إذا الروابط معطلة والرسالة تحتوي رابط => حذف الرسالة
    if not links_enabled:
        # تحقق وجود رابط بنمط بسيط
        if ("http://" in text.lower()) or ("https://" in text.lower()) or ("www." in text.lower()):
            # استثناء المشرفين والمالك
            if member.status not in ["administrator", "creator"]:
                await update.message.delete()