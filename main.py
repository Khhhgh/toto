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
OWNER_ID = 8011996271  # معرف مالك البوت

GROUPS_FILE = "groups.txt"

# تخزين معرف المجموعة
async def save_group(chat_id: int):
    if not os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "w") as f:
            pass
    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

# عند دخول البوت لمجموعة
async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        await save_group(chat.id)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id == OWNER_ID:
        owner_text = (
            "👑 أهلًا يا مالك البوت!\n\n"
            "هنا قائمة الأوامر الخاصة بالمالك فقط:\n"
            "- /broadcast <رسالة> : إرسال رسالة لكل المجموعات\n"
            "- /stats : إحصائيات البوت\n"
            "- ...\n\n"
            "يمكنك التحكم الكامل في البوت من هنا."
        )
        await context.bot.send_message(chat_id=chat_id, text=owner_text)
    else:
        welcome_text = (
            "👋 مرحبًا بك في بوت الحماية والألعاب!\n\n"
            "أنا هنا لأساعدك في إدارة مجموعتك وحمايتها، بالإضافة إلى توفير ألعاب ترفيهية.\n\n"
            "اختر من الأزرار أدناه للبدء:"
        )

        buttons = [
            [InlineKeyboardButton("➕ أضفني إلى مجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("📩 راسل المطور", url="https://t.me/T_4IJ")],
            [InlineKeyboardButton("📜 عرض الأوامر", callback_data="show_commands")]
        ]

        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)

# broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ هذا الأمر خاص بالمالك فقط.")
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

    sent_count = 0
    failed_count = 0

    for group_id in groups:
        try:
            await context.bot.send_message(chat_id=int(group_id), text=message)
            sent_count += 1
            await asyncio.sleep(0.1)  # لتخفيف الضغط على API
        except Exception:
            failed_count += 1

    await update.message.reply_text(f"✅ تم الإرسال إلى {sent_count} مجموعة.\n❌ فشل الإرسال في {failed_count} مجموعة.")

# زر عرض الأوامر
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_commands":
        await commands_list.show_commands(update, context)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # /start
    app.add_handler(CommandHandler("start", start))
    # /broadcast
    app.add_handler(CommandHandler("broadcast", broadcast))

    # استقبال دخول البوت إلى المجموعات
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    # أوامر خاصة لازم تيجي أولاً
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الالعاب$'), games.show_games))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الاوامر$'), commands_list.show_commands))

    # الأزرار (زر عرض الأوامر - الألعاب)
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(CallbackQueryHandler(games.handle_game_buttons))

    # حماية (بعد الأوامر الخاصة)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), protection.handle_text_commands))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_filter.link_chat_control))

    # فلتر روابط شامل
    app.add_handler(MessageHandler(filters.ALL, link_filter.filter_messages))

    print("✅ البوت شغال...")
    app.run_polling()
