from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
import os
import asyncio
import admin
import replies
import spam

TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 8011996271
USERS_FILE = "users.txt"
GROUPS_FILE = "groups.txt"

async def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

async def save_group(chat_id: int):
    if not os.path.exists(GROUPS_FILE):
        open(GROUPS_FILE, "w").close()
    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

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
        except Exception:
            return False
    return True

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
            ch_username = ch
            if ch.startswith("@"):
                ch_username = ch
            else:
                ch_username = "@" + ch
            buttons.append([InlineKeyboardButton(text=f"اشترك في {ch_username}", url=f"https://t.me/{ch_username.lstrip('@')}")])
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("🚫 يرجى الاشتراك في القنوات التالية ثم أرسل /start مجددًا:", reply_markup=keyboard)
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

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_group(update.effective_chat.id)
    state = admin.load_state()
    if state.get("welcome_enabled", True):
        for member in update.message.new_chat_members:
            await update.message.reply_text(f"أهلاً وسهلاً {member.mention_html()} 🎉", parse_mode="HTML")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await spam.filter_spam(update, context):
        return
    await replies.get_reply(update, context)

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin.handle_admin_text(update, context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    app.add_handler(CommandHandler("admin", admin.show_admin_panel))
    app.add_handler(CallbackQueryHandler(admin.handle_admin_buttons))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_admin_text))
    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
