from telegram import Update
from telegram.ext import ContextTypes

id_locked = False

async def lock_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global id_locked
    id_locked = True
    await update.message.reply_text("🔒 تم قفل أمر ايدي")

async def unlock_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global id_locked
    id_locked = False
    await update.message.reply_text("🔓 تم فتح أمر ايدي")

async def reply_to_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    text = (
        f"𖡋 𝐔𝐒𝐄 ⌯ @{user.username or user.first_name} 𖡋\n"
        f"𖡋 𝐌𝐒𝐆 ⌯ {update.message.message_id} 𖡋\n"
        f"𖡋 𝐒𝐓𝐀 ⌯ {'مالك اساسي' if user.id == 8011996271 else 'عضو'} 𖡋\n"
        f"𖡋 𝐈𝐃 ⌯ {user.id} 𖡋\n"
        f"𖡋 𝐄𝐃𝐈𝐓 ⌯ {update.message.edit_date or '0'} 𖡋\n"
        f"𖡋 𝐂𝐑 ⌯ {user.date.strftime('%Y/%m/%d')} 𖡋"
    )

    photo_url = "https://i.ibb.co/7NqtVwx/IMG-20201116-WA0020.jpg"

    await context.bot.send_photo(chat_id=chat.id, photo=photo_url, caption=text)
