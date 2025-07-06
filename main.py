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
USERS_FILE = "users.txt"  # ملف لتخزين المستخدمين الذين بدأوا مع البوت

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

# تخزين معرف المستخدم الجديد
async def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            pass
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")
        return True  # مستخدم جديد
    return False  # مستخدم موجود مسبقاً

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # تحقق إذا المستخدم جديد
    is_new_user = await save_user(user_id)

    # إذا المستخدم جديد، ارسل للمالك رسالة
    if is_new_user:
        user_name = update.effective_user.username or update.effective_user.first_name
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"👤 مستخدم جديد بدأ مع البوت:\n- الاسم: {user_name}\n- المعرف: {user_id}"
        )

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
            [InlineKeyboardButton("📩 راسل المطور", url="https://t.me/T_4IJ")]
        ]

        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)

# باقي الكود كما هو (broadcast, handle_buttons, إلخ)...

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الالعاب$'), games.show_games))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^الاوامر$'), commands_list.show_commands))

    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(CallbackQueryHandler(games.handle_game_buttons))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), protection.handle_text_commands))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_filter.link_chat_control))

    app.add_handler(MessageHandler(filters.ALL, link_filter.filter_messages))

    print("✅ البوت شغال...")
    app.run_polling()
