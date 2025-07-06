from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import asyncio
import os

# استيراد الوحدات الخارجية
import protection
import games
import link_filter
import commands_list
import replies
import id_lock_handlers
import admin  # لوحة تحكم المالك

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 8011996271

GROUPS_FILE = "groups.txt"
USERS_FILE = "users.txt"

# حفظ معرف المجموعة
async def save_group(chat_id: int):
    if not os.path.exists(GROUPS_FILE):
        open(GROUPS_FILE, "w").close()
    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

# حفظ المستخدمين
async def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

# عند انضمام البوت لمجموعة
async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        await save_group(chat.id)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    await save_user(user.id)

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
    await context.bot.send_message(chat_id=chat.id, text=welcome_text, reply_markup=keyboard)

# تفعيل البوت في المجموعة
async def activate_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status in ["administrator", "creator"]:
        await update.message.reply_text("✅ تم تفعيل البوت في هذه المجموعة.")
        await save_group(chat.id)

# الرد على "ايدي"
async def reply_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if id_lock_handlers.id_locked:
        return
    text = update.message.text
    if text == "ايدي":
        await id_lock_handlers.reply_to_id(update, context)

# الردود الجاهزة
async def reply_to_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = replies.get_reply(text)
    if response:
        await update.message.reply_text(response)

# عرض الألعاب
async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "الالعاب":
        games_list = (
            "🎮 ألعاب البوت:\n"
            "1. اكس او\n"
            "2. خمن\n"
            "3. الاسرع\n\n"
            "ارسل اسم اللعبة للبدء."
        )
        await update.message.reply_text(games_list)

# بدء لعبة
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ["اكس او", "خمن", "الاسرع"]:
        await games.start_game_by_name(update, context, text)

# تشغيل البوت
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # أوامر أساسية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin.show_admin_panel))

    # لوحة تحكم المالك
    app.add_handler(CallbackQueryHandler(admin.handle_admin_buttons))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), admin.handle_admin_text))

    # انضمام مجموعة
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    # تفعيل البوت
    app.add_handler(MessageHandler(filters.Regex(r"^تفعيل$"), activate_bot))

    # الألعاب
    app.add_handler(MessageHandler(filters.Regex(r"^الالعاب$"), show_games))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^(اكس او|خمن|الاسرع)$"), start_game))

    # ايدي
    app.add_handler(MessageHandler(filters.Regex(r"^ايدي$"), reply_id))

    # الردود
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_messages))

    # الحماية والفلاتر
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), protection.handle_text_commands))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_filter.link_chat_control))
    app.add_handler(MessageHandler(filters.ALL, link_filter.filter_messages))

    print("✅ البوت شغال بنجاح...")
    app.run_polling()
