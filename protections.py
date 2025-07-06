from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

# تحقق اذا المستخدم مشرف أو مالك
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# الحصول على معرف العضو الهدف من الرد
async def get_target_user_id(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id
    return None

# كتم العضو
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ هذا الأمر للمشرفين فقط")
    user_id = await get_target_user_id(update)
    if not user_id:
        return await update.message.reply_text("❌ الرجاء الرد على العضو للكتم")
    try:
        perms = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions=perms)
        await update.message.reply_text("✅ تم كتم العضو")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ في الكتم: {e}")

# فك كتم العضو
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ هذا الأمر للمشرفين فقط")
    user_id = await get_target_user_id(update)
    if not user_id:
        return await update.message.reply_text("❌ الرجاء الرد على العضو لفك الكتم")
    try:
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions=perms)
        await update.message.reply_text("✅ تم فك الكتم عن العضو")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ في فك الكتم: {e}")

# طرد العضو
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ هذا الأمر للمشرفين فقط")
    user_id = await get_target_user_id(update)
    if not user_id:
        return await update.message.reply_text("❌ الرجاء الرد على العضو للطرد")
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)  # لفك الحظر الفوري والطرد فقط
        await update.message.reply_text("✅ تم طرد العضو")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ في الطرد: {e}")

# حظر العضو
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ هذا الأمر للمشرفين فقط")
    user_id = await get_target_user_id(update)
    if not user_id:
        return await update.message.reply_text("❌ الرجاء الرد على العضو للحظر")
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("✅ تم حظر العضو")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ في الحظر: {e}")

# فك حظر العضو
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ هذا الأمر للمشرفين فقط")
    user_id = await get_target_user_id(update)
    if not user_id:
        return await update.message.reply_text("❌ الرجاء الرد على العضو لفك الحظر")
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("✅ تم فك الحظر عن العضو")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ في فك الحظر: {e}")

# رفع مشرف
async def promote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ فقط المشرفين يمكنهم الرفع")
    user_id = await get_target_user_id(update)
    if not user_id:
        return await update.message.reply_text("❌ الرجاء الرد على العضو للرفع")
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id,
            user_id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False,
        )
        await update.message.reply_text("✅ تم رفع العضو مشرف")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ في الرفع: {e}")

# تنزيل مشرف
async def demote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ فقط المشرفين يمكنهم التنزيل")
    user_id = await get_target_user_id(update)
    if not user_id:
        return await update.message.reply_text("❌ الرجاء الرد على العضو للتنزيل")
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id,
            user_id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
        )
        await update.message.reply_text("✅ تم تنزيل العضو من المشرفية")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ في التنزيل: {e}")

# عرض قائمة الأوامر التعليمية
async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📋 *قائمة أوامر الحماية بالرد على العضو (بدون /):*

- كتم  
  ➜ كتم العضو والعضو ما يقدر يرسل رسائل.

- طرد  
  ➜ طرد العضو من المجموعة.

- الغاء كتم  
  ➜ فك كتم العضو.

- حظر  
  ➜ حظر العضو من المجموعة.

- الغاء حظر  
  ➜ فك الحظر عن العضو.

- رفع مشرف  
  ➜ رفع العضو مشرف.

- تنزيل مشرف  
  ➜ تنزيل العضو من المشرفين.

- قفل الروابط  
  ➜ قفل ارسال الروابط في المجموعة.

- فتح الروابط  
  ➜ فتح ارسال الروابط في المجموعة.

---

*لتنفيذ أي أمر، فقط رد على رسالة العضو واكتب الأمر بالضبط بدون شرطه /.*
"""
    await update.message.reply_text(text)
