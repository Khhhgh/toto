from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import asyncio
import os
import games
import replies
import admin
import welcome

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 8011996271

GROUPS_FILE = "groups.txt"
USERS_FILE = "users.txt"

async def save_group(chat_id: int):
    if not os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "w"): pass
    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\\n")

async def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w"): pass
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await save_user(user_id)

    welcome_text = (
        "اهلين انا ماريا↞ اختصاصي ادارة المجموعات من السبام والخ..↞ كت تويت, يوتيوب, ساوند , واشياء كثير ..↞ عشان تفعلني ارفعني اشراف وارسل تفعيل."
    )
    buttons = [
        [{"text": "ضيفني لمجموعتك ✨😺", "url": f"https://t.me/{context.bot.username}?startgroup=true"}],
        [{"text": "📩 راسل المطور", "url": "https://t.me/T_4IJ"}]
    ]
    keyboard = welcome.make_keyboard(buttons)
    await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)

async def new_member_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await save_group(update.effective_chat.id)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    await save_user(user_id)

    # الردود العامة
    await replies.handle_replies(update, context)

    # ألعاب
    if text == "الالعاب":
        await games.show_games(update, context)
        return

    if text == "خمن":
        await games.start_guess_game(update, context)
        return

    if text == "الاسرع":
        await games.start_fast_game(update, context)
        return

    if text == "اكس او":
        await games.start_ttt(update, context)
        return

    # تشغيل الألعاب
    await games.handle_guess(update, context)
    await games.handle_fast(update, context)
    await games.handle_ttt(update, context)

    # أوامر مالك البوت
    if text == "/admin" and user_id == OWNER_ID:
        await admin.show_admin_panel(update, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_notify))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(CallbackQueryHandler(admin.handle_admin_buttons))

    print("✅ البوت شغال...")
    app.run_polling()
