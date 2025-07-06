from telegram import Update
from telegram.ext import ContextTypes

OWNER_ID = 8011996271

PROFILE_IMAGE = "profile.jpg"  # تأكد ترفعها مع ملفات البوت

user_message_counts = {}

async def handle_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else user.first_name
    msg_count = user_message_counts.get(user_id, 12)
    edit_count = 0
    status = "مالك أساسي" if user_id == OWNER_ID else "عضو عادي"
    create_date = "2020/11/01"
    
    info_text = (
        f"𖡋 𝐔𝐒𝐄 ⌯ {username}\n"
        f"𖡋 𝐌𝐒𝐆 ⌯ {msg_count}\n"
        f"𖡋 𝐒𝐓𝐀 ⌯ {status}\n"
        f"𖡋 𝐈𝐃 ⌯ {user_id}\n"
        f"𖡋 𝐄𝐃𝐈𝐓 ⌯ {edit_count}\n"
        f"𖡋 𝐂𝐑  ⌯ {create_date}"
    )
    
    with open(PROFILE_IMAGE, "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=info_text
        )
