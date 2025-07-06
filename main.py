from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import os
import asyncio
from telegram.error import BadRequest

import admin  # استيراد ملف لوحة تحكم المالك (admin.py)
import replies  # ملف الردود الجاهزة


TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 8011996271

USERS_FILE = "users.txt"
GROUPS_FILE = "groups.txt"

# حفظ المستخدم
async def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

# حفظ المجموعة
async def save_group(chat_id: int):
    if not os.path.exists(GROUPS_FILE):
        open(GROUPS_FILE, "w").close()
    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

# تحقق من اشتراك المستخدم في القنوات الإلزامية
async def check_subscription(user_id, bot):
    state = admin.load_state()
    channels = state.get("subscription_channels", [])
    if not channels:
        # لا توجد قنوات اشتراك، نسمح بالوصول
        return True

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except BadRequest:
            # البوت ليس عضو في القناة أو معرف القناة خاطئ
            return False
    return True

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # حفظ المستخدم
    await save_user(user.id)

    # تحميل حالة البوت
    state = admin.load_state()
    if not state.get("bot_enabled", True):
        await update.message.reply_text("⛔ البوت معطل حالياً.")
        return

    # تحقق الاشتراك في القنوات
    is_subscribed = await check_subscription(user.id, context.bot)
    if not is_subscribed:
        channels = state.get("subscription_channels", [])
        buttons = []
        for ch in channels:
            ch_username = ch if ch.startswith("@") else "@" + ch
            buttons.append([InlineKeyboardButton(text=f"اشترك في {ch_username}", url=f"https://t.me/{ch_username.lstrip('@')}")])
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "🚫 يرجى الاشتراك في القنوات التالية أولًا ثم أرسل /start مجددًا:",
            reply_markup=keyboard
        )
        return

    # رسالة الترحيب مع أزرار
    welcome_text = (
        "اهلين انا ماريا ↞ اختصاصي إدارة المجموعات من السبام والخ...\n"
        "↞ كت تويت، يوتيوب، ساوند، وأشياء كثير...\n"
        "↞ عشان تفعلني ارفعني اشراف وارسل تفعيل."
    )
    buttons = [
        [InlineKeyboardButton("ضيفني لمجموعتك ✨😺", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("📩 راسل المطور", url="https://t.me/T_4IJ")],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat.id, welcome_text, reply_markup=keyboard)

# الترحيب بانضمام أعضاء جدد للمجموعات
async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = admin.load_state()
    if not state.get("welcome_enabled", True):
        return  # إذا الترحيب معطل ما نرسل شيء

    for member in update.message.new_chat_members:
        await update.message.reply_text(f"أهلاً ومرحباً بك يا {member.mention_html()} في المجموعة 🎉", parse_mode="HTML")

# استقبال انضمام بوت لمجموعة جديدة
async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        await save_group(chat.id)

# التعامل مع الردود الجاهزة
async def handle_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    reply = replies.get_reply(text)
    if reply:
        await update.message.reply_text(reply)

# التعامل مع حماية السبام (مثال)
async def handle_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await spam.filter_spam(update, context):
        # تم حظر الرسالة كسبام
        return True
    return False

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فلترة السبام أولاً
    if await handle_spam(update, context):
        return

    # الردود الجاهزة
    await handle_replies(update, context)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(TOKEN).build()

    # تسجيل المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    # ردود النصوص والفلترة
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))

    # لوحة تحكم المالك
    app.add_handler(CommandHandler("admin", admin.show_admin_panel))
    app.add_handler(CallbackQueryHandler(admin.handle_admin_buttons))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), admin.handle_admin_text))

    print("✅ البوت شغال...")
    app.run_polling()
