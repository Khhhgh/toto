from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import os
import asyncio

import replies
import id_info

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 8011996271

ID_LOCK_FILE = "id_lock.txt"
GROUPS_FILE = "groups.txt"


def read_id_lock():
    if not os.path.exists(ID_LOCK_FILE):
        with open(ID_LOCK_FILE, "w") as f:
            f.write("1")  # مفعّل بشكل افتراضي
        return True
    with open(ID_LOCK_FILE, "r") as f:
        status = f.read().strip()
    return status == "1"


def write_id_lock(value: bool):
    with open(ID_LOCK_FILE, "w") as f:
        f.write("1" if value else "0")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    welcome_text = (
        "اهلين انا ماريا↞ اختصاصي ادارة المجموعات من السبام والخ..↞ "
        "كت تويت, يوتيوب, ساوند , واشياء كثير ..↞ "
        "عشان تفعلني ارفعني اشراف وارسل تفعيل."
    )

    buttons = [
        [InlineKeyboardButton("ضيفني لمجموعتك ✨😺", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("📩 راسل المطور", url="https://t.me/T_4IJ")],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)


async def save_group(chat_id: int):
    if not os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "w") as f:
            pass
    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")


async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        await save_group(chat.id)


async def lock_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ هذا الأمر للمالك فقط.")
        return
    write_id_lock(False)
    await update.message.reply_text("✅ تم تعطيل الرد على كلمة ايدي.")


async def unlock_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ هذا الأمر للمالك فقط.")
        return
    write_id_lock(True)
    await update.message.reply_text("✅ تم تفعيل الرد على كلمة ايدي.")


async def handle_id_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if read_id_lock():
        await id_info.handle_id_command(update, context)
    else:
        # لا رد إذا معطل
        pass


async def handle_general_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() == "ايدي":
        return
    reply = replies.get_reply(text)
    if reply:
        await update.message.reply_text(reply)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    app.add_handler(CommandHandler("قفل_الايدي", lock_id))
    app.add_handler(CommandHandler("فتح_الايدي", unlock_id))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^ايدي$'), handle_id_wrapper))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_general_replies))

    print("✅ البوت شغال...")
    app.run_polling()
