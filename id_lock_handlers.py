from telegram import Update
from telegram.ext import ContextTypes

# حالة القفل مبدئياً مفتوح
id_locked = False

# لتفعيل أو تعطيل أمر الايدي
allow_id_command = True

async def lock_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global id_locked
    user = update.effective_user
    chat = update.effective_chat

    # فقط مالك البوت يقدر يقفل الايدي
    if user.id != 8011996271:
        await update.message.reply_text("❌ هذا الأمر خاص بالمالك فقط.")
        return

    id_locked = True
    await update.message.reply_text("✅ تم قفل أمر الايدي. لن يتم الرد عليه حتى يتم فتحه.")

async def unlock_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global id_locked
    user = update.effective_user
    chat = update.effective_chat

    # فقط مالك البوت يقدر يفتح الايدي
    if user.id != 8011996271:
        await update.message.reply_text("❌ هذا الأمر خاص بالمالك فقط.")
        return

    id_locked = False
    await update.message.reply_text("✅ تم فتح أمر الايدي. سيتم الرد عليه الآن.")

async def reply_to_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global id_locked
    if id_locked:
        return  # لا يرد إذا كانت القفل مفعّل

    user = update.effective_user
    chat = update.effective_chat
    user_id = user.id
    username = f"@{user.username}" if user.username else user.first_name
    first_name = user.first_name
    last_name = user.last_name if user.last_name else ""
    full_name = f"{first_name} {last_name}".strip()
    message_id = update.message.message_id

    # مثال بيانات يمكن تعديلها حسب المطلوب
    text = (
        f"𖡋 𝐔𝐒𝐄 ⌯  {username} \n"
        f"𖡋 𝐌𝐒𝐆 ⌯  {update.message.text}\n"
        f"𖡋 𝐒𝐓𝐀 ⌯  {'مالك اساسي' if user_id == 8011996271 else 'عضو'}\n"
        f"𖡋 𝐈𝐃 ⌯  {user_id}\n"
        f"𖡋 𝐄𝐃𝐈𝐓 ⌯  0\n"
        f"𖡋 𝐂𝐑 ⌯  2020/11\n"
    )

    # إرسال صورة مع النص (صورة افتراضية)
    photo_url = "https://i.imgur.com/yourimage.jpg"  # عدلها برابط صورة تناسبك
    await context.bot.send_photo(chat_id=chat.id, photo=photo_url, caption=text)
