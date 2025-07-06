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

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 8011996271

GROUPS_FILE = "groups.txt"
USERS_FILE = "users.txt"

# تخزين معرف المجموعة
async def save_group(chat_id: int):
    if not os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "w"): pass
    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

# تخزين المستخدم الجديد
async def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w"): pass
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")
        return True
    return False

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    is_new_user = await save_user(user_id)
    if is_new_user:
        username = update.effective_user.username or update.effective_user.first_name
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"👤 مستخدم جديد بدأ البوت:\n- الاسم: {username}\n- ID: {user_id}"
        )

    if user_id == OWNER_ID:
        owner_text = (
            "👑 أهلًا مالك البوت!\n\n"
            "- /broadcast <رسالة> لإرسالها لجميع المجموعات\n"
            "- /stats (قريبًا)..."
        )
        await context.bot.send_message(chat_id=chat_id, text=owner_text)
    else:
        welcome_text = (
            "👋 مرحبًا بك في بوت الحماية والألعاب!\n\n"
            "أنا هنا لأساعدك في إدارة مجموعتك وحمايتها، وأقدم لك ألعاب ترفيهية ممتعة!"
        )
        buttons = [
            [InlineKeyboardButton("➕ أضفني إلى مجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("📩 راسل المطور", url="https://t.me/T_4IJ")]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)

# broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ هذا الأمر للمالك فقط.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❗ استخدم: /broadcast <الرسالة>")
        return

    message = " ".join(context.args)

    if not os.path.exists(GROUPS_FILE):
        await update.message.reply_text("⚠️ لا توجد مجموعات مسجلة بعد.")
        return

    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()

    sent = 0
    failed = 0

    for gid in groups:
        try:
            await context.bot.send_message(chat_id=int(gid), text=message)
            sent += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1

    await update.message.reply_text(f"✅ تم الإرسال إلى {sent} مجموعة.\n❌ فشل في {failed} مجموعة.")

# التعامل مع الأزرار التفاعلية (حالياً لا توجد)
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, save_group))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الالعاب$'), games.show_games))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الاوامر$'), commands_list.show_commands))

    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(CallbackQueryHandler(games.handle_game_buttons))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), protection.handle_text_commands))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_filter.link_chat_control))

    app.add_handler(MessageHandler(filters.ALL, link_filter.filter_messages))

    print("✅ البوت شغال...")
    app.run_polling()
