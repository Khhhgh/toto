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
from telegram.error import BadRequest

import admin

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

# تحقق الاشتراك
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

# /start
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
            buttons.append([
                InlineKeyboardButton(f"اشترك في {ch_username}", url=f"https://t.me/{ch_username.lstrip('@')}")
            ])
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("🚫 اشترك بالقنوات التالية ثم أرسل /start:", reply_markup=keyboard)
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
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

# تفعيل
async def activate_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status in ["administrator", "creator"]:
        await save_group(chat.id)
        await update.message.reply_text("✅ تم تفعيل البوت في هذه المجموعة.")
    else:
        await update.message.reply_text("❌ فقط المشرفين يمكنهم تنفيذ هذا الأمر.")

# ترحيب بالأعضاء الجدد
async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    new_members = update.message.new_chat_members
    await save_group(chat.id)
    state = admin.load_state()

    if state.get("welcome_enabled", True):
        for member in new_members:
            if member.id != context.bot.id:
                await update.message.reply_text(
                    f"👋 أهلًا وسهلًا {member.mention_html()} نورت المجموعة!",
                    parse_mode="HTML"
                )

# الردود الجاهزة للجروبات
async def reply_to_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "ايدي":
        await update.message.reply_text(f"🆔 ايديك: {update.effective_user.id}")
    elif text.lower() in ["شلونك", "شلونج", "شلونكم"]:
        await update.message.reply_text("تمام وانت؟ 😄")
    elif text.lower() == "باي":
        await update.message.reply_text("مع السلامة 🖐️")
    # أضف ردود أكثر إذا تريد

# تشغيل البوت
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(TOKEN).build()

    # أوامر عامة
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r"^تفعيل$"), activate_bot))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    # لوحة تحكم المالك
    app.add_handler(CommandHandler("admin", admin.show_admin_panel))
    app.add_handler(CallbackQueryHandler(admin.handle_admin_buttons))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, admin.handle_admin_text))

    # الردود العامة في الجروبات
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, reply_to_messages))

    print("✅ البوت شغال...")
    app.run_polling()
