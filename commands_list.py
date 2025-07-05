from telegram import Update
from telegram.ext import ContextTypes

async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    commands_text = (
        "📜 *قائمة الأوامر المتاحة:* \n\n"
        "🔹 كتم — للرد على رسالة كتم المستخدم\n"
        "🔹 فك كتم / الغاء كتم — لفك الكتم\n"
        "🔹 طرد — لطرد المستخدم المردود عليه\n"
        "🔹 حظر — لحظر المستخدم\n"
        "🔹 فتح الروابط — لتفعيل الروابط في المجموعة\n"
        "🔹 تعطيل الروابط — لمنع الروابط في المجموعة\n"
        "🔹 فتح الدردشة — للسماح للجميع بالكتابة\n"
        "🔹 غلق الدردشة — لمنع الأعضاء من الكتابة\n"
        "🔹 الالعاب — لعرض قائمة الألعاب الترفيهية\n"
        "🔹 /broadcast <رسالة> — أمر خاص بالمالك لإرسال رسالة لجميع المجموعات\n"
        "\n*ملاحظة:* بعض الأوامر تحتاج أن تكون مشرف أو مالك المجموعة."
    )

    await update.message.reply_text(commands_text, parse_mode="Markdown")