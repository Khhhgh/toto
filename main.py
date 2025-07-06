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

import admin  # تأكد أن ملف admin.py موجود بنفس المجلد

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

# تحقق من اشتراك المستخدم في القنوات
async def check_subscription(user_id, bot):
    state = admin.load_state()
    channels = state.get("subscription_channels", [])
    if not channels:
        return True

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except BadRequest:
            return False
    return True

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    await save_user(user.id)

    state = admin.load_state()
    if not state.get("bot_enabled", True):
        await update.message.reply_text("⛔ البوت معطل حالياً.")
        return

    is_subscribed = await check_subscription(user.id, context.bot)
    if not is_subscribed:
        channels = state.get("subscription_channels", [])
        buttons = []
        for ch in channels:
            ch_username = ch if ch.startswith("@") else "@" + ch
            buttons.append([InlineKeyboardButton(text=f"اشترك في {ch_username}", url=f"https://t.me/{ch_username.lstrip('@')}")])
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "🚫 يرجى الاشتراك في القنوات التالية أولاً ثم أرسل /start مجددًا:",
            reply_markup=keyboard
        )
        return

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

# أمر "تفعيل"
async def activate_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status in ["administrator", "creator"]:
        await update.message.reply_text("✅ تم تفعيل البوت في هذه المجموعة.")
        await save_group(chat.id)
    else:
        await update.message.reply_text("❌ فقط المشرفين يمكنهم استخدام هذا الأمر.")

# ترحيب بالمجموعة الجديدة
async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        await save_group(chat.id)
        state = admin.load_state()
        if state.get("welcome_enabled", True):
            await update.message.reply_text("👋 تم انضمام البوت للمجموعة بنجاح!")

# رسالة تجريبية لأي نص داخل الجروب
async def handle_group_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        await update.message.reply_text("✅ البوت شغال داخل الجروب!")

# تشغيل البوت
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin.show_admin_panel))
    app.add_handler(CallbackQueryHandler(admin.handle_admin_buttons))
    app.add_handler(MessageHandler(filters.Regex(r"^تفعيل$"), activate_bot))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), admin.handle_admin_text))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_group_text))

    print("✅ البوت شغال...")
    app.run_polling()
