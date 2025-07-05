from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
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

import protection
import games
import link_filter
import commands_list

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 8011996271  # معرف مالك البوت

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
            [
                InlineKeyboardButton(
                    text="➕ أضفني إلى مجموعتك",
                    url=f"https://t.me/{context.bot.username}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📩 راسل المطور",
                    url="https://t.me/T_4IJ",
                )
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ هذا الأمر خاص بالمالك فقط.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❗ استخدم: /broadcast <الرسالة>")
        return

    message = " ".join(context.args)
    # هنا تقدر تضيف إرسال الرسالة لجميع المجموعات (تحتاج حفظهم في قاعدة بيانات)
    await update.message.reply_text(f"تم إرسال الرسالة:\n\n{message}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # ربط ملف الحماية
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), protection.handle_text_commands))

    # ربط ملف الألعاب
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الالعاب$'), games.show_games))
    app.add_handler(CallbackQueryHandler(games.handle_game_buttons))

    # ربط ملف تحكم الروابط والدردشة
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_filter.link_chat_control))
    app.add_handler(MessageHandler(filters.ALL, link_filter.filter_messages))

    # ربط ملف قائمة الأوامر
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الاوامر$'), commands_list.show_commands))

    print("البوت شغال...")
    app.run_polling()