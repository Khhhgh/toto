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

import protection
import games
import link_filter
import commands_list
import replies
import id_lock_handlers
import admin  # استيراد ملف لوحة تحكم المالك

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"  
OWNER_ID = 8011996271  

GROUPS_FILE = "groups.txt"

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    welcome_text = (
        "اهلين انا ماريا↞ اختصاصي ادارة المجموعات من السبام والخ..↞ كت تويت, يوتيوب, ساوند , واشياء كثير ..↞ عشان تفعلني ارفعني اشراف وارسل تفعيل."
    )

    buttons = [
        [InlineKeyboardButton("ضيفني لمجموعتك ✨😺", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("📩 راسل المطور", url="https://t.me/T_4IJ")],
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)

async def activate_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat
    user = update.effective_user
    if msg.text == "تفعيل":
        member = await chat.get_member(user.id)
        if member.status in ["administrator", "creator"]:
            await update.message.reply_text("تم تفعيل الكروب 😊")
            await save_group(chat.id)

async def reply_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if id_lock_handlers.id_locked:
        return
    text = update.message.text
    if text == "ايدي":
        await id_lock_handlers.reply_to_id(update, context)

async def reply_to_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = replies.get_reply(text)
    if response:
        await update.message.reply_text(response)

async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "الالعاب":
        games_list = (
            "🎮 ألعاب البوت:\n"
            "1. اكس او\n"
            "2. خمن\n"
            "3. الاسرع\n"
            "\nارسل اسم اللعبة للبدء."
        )
        await update.message.reply_text(games_list)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ["اكس او", "خمن", "الاسرع"]:
        await games.start_game_by_name(update, context, text)

# تغليف معالج نصوص الادمن ليشتغل فقط إذا الادمن داخل وضع انتظار معين
async def admin_text_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    waiting_keys = [
        "waiting_for_channel_add",
        "waiting_broadcast_groups",
        "waiting_broadcast_private",
        "waiting_promote",
        "waiting_demote",
    ]
    if not any(context.user_data.get(k) for k in waiting_keys):
        return
    await admin.handle_admin_text(update, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # أوامر أساسية
    app.add_handler(CommandHandler("start", start))

    # لوحة تحكم المالك
    app.add_handler(CommandHandler("admin", admin.show_admin_panel))
    app.add_handler(CallbackQueryHandler(admin.handle_admin_buttons))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), admin_text_wrapper))

    # حفظ المجموعات عند انضمام البوت
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    # تفعيل البوت بالكروب
    app.add_handler(MessageHandler(filters.Regex(r'^تفعيل$'), activate_bot))

    # ألعاب
    app.add_handler(MessageHandler(filters.Regex(r'^الالعاب$'), show_games))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^(اكس او|خمن|الاسرع)$'), start_game))

    # الرد على كلمة ايدي
    app.add_handler(MessageHandler(filters.Regex(r'^ايدي$'), reply_id))

    # الردود الجاهزة
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_messages))

    # باقي الفلاتر
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), protection.handle_text_commands))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_filter.link_chat_control))
    app.add_handler(MessageHandler(filters.ALL, link_filter.filter_messages))

    print("✅ البوت شغال...")
    app.run_polling()
