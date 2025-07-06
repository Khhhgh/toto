from telegram import Update
from telegram.ext import ContextTypes

# كلمات ممنوعة (عدل حسب الحاجة)
BAD_WORDS = ["spamword1", "spamword2", "رابط ممنوع", "كلمة ممنوعة"]

# كلمات روابط سبام ممنوعة
SPAM_LINKS_KEYWORDS = ["t.me/", "telegram.me/", "joinchat/", "discord.gg/"]

async def spam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return
    text = update.message.text.lower()

    # حذف الرسائل التي تحتوي روابط ممنوعة
    if any(link in text for link in SPAM_LINKS_KEYWORDS):
        await update.message.delete()
        await update.message.reply_text("🚫 ممنوع نشر روابط هنا!")
        return

    # حذف الرسائل التي تحتوي كلمات ممنوعة
    if any(bad_word in text for bad_word in BAD_WORDS):
        await update.message.delete()
        await update.message.reply_text("🚫 هذه الكلمة ممنوعة هنا!")
        return
