from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

async def is_admin(update: Update):
    user_id = update.effective_user.id
    chat = update.effective_chat
    member = await chat.get_member(user_id)
    return member.status in ["administrator", "creator"]

async def handle_text_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    text = update.message.text.lower()
    reply = update.message.reply_to_message
    if not reply:
        return  # لازم يكون رد على رسالة

    if not await is_admin(update):
        return  # فقط المشرفين والمالك

    user = reply.from_user

    if text == "كتم":
        try:
            await update.effective_chat.restrict_member(
                user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=None,
            )
            await update.message.reply_text(f"🔇 تم كتم {user.full_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")

    elif text in ["فك كتم", "الغاء كتم"]:
        try:
            await update.effective_chat.restrict_member(
                user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
                until_date=None,
            )
            await update.message.reply_text(f"🔊 تم فك كتم {user.full_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")

    elif text == "طرد":
        try:
            await update.effective_chat.ban_member(user.id)
            await update.message.reply_text(f"🚫 تم طرد {user.full_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")

    elif text == "حظر":
        try:
            await update.effective_chat.ban_member(user.id)
            await update.message.reply_text(f"⛔ تم حظر {user.full_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")