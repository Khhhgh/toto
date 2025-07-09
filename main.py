import logging
import asyncio
import nest_asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# تفعيل nest_asyncio لتفادي مشكلة "This event loop is already running"
nest_asyncio.apply()

# إعدادات التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# توكن البوت
TOKEN = "6477545499:AAHkCgwT5Sn1otiMst_sAOmoAp_QC1_ILzA"  # استبدله بتوكن البوت الخاص بك

# معرف المالك
OWNER_ID = 1310488710  # استبدله بمعرفك الحقيقي

# قناة الاشتراك الإجباري
mandatory_channel = None
notify_new_users = True  # إشعار دخول المستخدمين الجدد مفعل بشكل افتراضي

# قائمة لتخزين معرفات المستخدمين
user_ids = set()

# دالة لعرض الأزرار للمستخدم
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if mandatory_channel:
        member = await update.bot.get_chat_member(mandatory_channel, update.message.from_user.id)
        if member.status not in ['member', 'administrator']:
            await update.message.reply_text(f"⚠️ يجب عليك الاشتراك في القناة: {mandatory_channel}\nيمكنك الاشتراك عبر هذا الرابط: https://t.me/{mandatory_channel[1:]}")
            return

    user_ids.add(update.message.from_user.id)

    welcome_message = (
        "👋 مرحبًا! أنا بوت لتحميل الفيديوهات 🎥\n\n"
        "اختر الموقع الذي تريد تنزيل الفيديو منه 💻👇\n\n"
        "إذا كنت بحاجة إلى المساعدة، تواصل مع المطور عبر الزر أدناه 👨‍💻"
    )

    keyboard = [
        [InlineKeyboardButton("تحميل من يوتيوب 📹", callback_data='youtube')],
        [InlineKeyboardButton("تحميل من تيك توك 🎶", callback_data='tiktok')],
        [InlineKeyboardButton("تحميل من فيسبوك 📘", callback_data='facebook')],
        [InlineKeyboardButton("تحميل من انستجرام 📸", callback_data='instagram')],
        [InlineKeyboardButton("تحميل من تويتر 🐦", callback_data='twitter')],
        [InlineKeyboardButton("تواصل مع المطور 📨", url="https://t.me/T_4IJ")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# دالة لإرسال رسالة إذاعة لجميع المستخدمين
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == OWNER_ID:
        message = ' '.join(context.args)
        if not message:
            await update.message.reply_text("⚠️ الرجاء إرسال رسالة للإذاعة.")
            return

        for user_id in user_ids:
            try:
                await update.bot.send_message(user_id, message)
            except Exception as e:
                logger.error(f"تعذر إرسال الرسالة للمستخدم {user_id}: {e}")

        await update.message.reply_text("✅ تم إرسال الرسالة بنجاح لجميع المستخدمين.")
    else:
        await update.message.reply_text("❌ أنت لست المالك!")

# دالة لإضافة قناة اشتراك إجباري
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == OWNER_ID:
        global mandatory_channel
        mandatory_channel = update.message.text.split(" ")[1]
        await update.message.reply_text(f"تم إضافة القناة بنجاح: {mandatory_channel}")
    else:
        await update.message.reply_text("❌ أنت لست المالك!")

# دالة لحذف قناة اشتراك إجباري
async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == OWNER_ID:
        global mandatory_channel
        mandatory_channel = None
        await update.message.reply_text("تم حذف القناة الاشتراك الإجباري.")
    else:
        await update.message.reply_text("❌ أنت لست المالك!")

# دالة لتفعيل إشعار دخول المستخدمين الجدد
async def welcome_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if notify_new_users:
        user_id = update.message.new_chat_members[0].id
        if user_id != OWNER_ID:
            await context.bot.send_message(chat_id=OWNER_ID, text=f"🔔 دخل مستخدم جديد إلى البوت: {update.message.new_chat_members[0].full_name}")

# دالة لتنزيل الفيديو أو الصوت بناءً على الموقع المختار
async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    site = context.user_data.get('site')

    if "http" not in url:
        await update.message.reply_text("⚠️ الرجاء إرسال رابط صالح!")
        return

    ydl_opts = {
        'format': 'best',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
    }

    if site == 'youtube':
        ydl_opts['extractor_args'] = {'youtube': {'noplaylist': True}}
    elif site == 'tiktok':
        ydl_opts['extractor_args'] = {'tiktok': {'download': True}}
    elif site == 'facebook':
        ydl_opts['extractor_args'] = {'facebook': {'download': True}}
    elif site == 'instagram':
        ydl_opts['extractor_args'] = {'instagram': {'download': True}}
    elif site == 'twitter':
        ydl_opts['extractor_args'] = {'twitter': {'download': True}}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)

            await update.message.reply_text(f"✅ تم تنزيل الفيديو من {site.capitalize()} بنجاح: {video_filename}")

            if 'audio' in info_dict['formats'][0]['ext']:
                await update.message.reply_audio(audio=open(video_filename, 'rb'))
            else:
                await update.message.reply_video(video=open(video_filename, 'rb'))

        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ أثناء تنزيل الفيديو من {site.capitalize()}: {str(e)}")

# معالجة الأزرار (التحكم في الأزرار)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == 'youtube':
        context.user_data['site'] = 'youtube'
        await query.edit_message_text("⚡ تم اختيار يوتيوب. الرجاء إرسال الرابط لتحميله.")
    elif data == 'tiktok':
        context.user_data['site'] = 'tiktok'
        await query.edit_message_text("⚡ تم اختيار تيك توك. الرجاء إرسال الرابط لتحميله.")
    elif data == 'facebook':
        context.user_data['site'] = 'facebook'
        await query.edit_message_text("⚡ تم اختيار فيسبوك. الرجاء إرسال الرابط لتحميله.")
    elif data == 'instagram':
        context.user_data['site'] = 'instagram'
        await query.edit_message_text("⚡ تم اختيار انستجرام. الرجاء إرسال الرابط لتحميله.")
    elif data == 'twitter':
        context.user_data['site'] = 'twitter'
        await query.edit_message_text("⚡ تم اختيار تويتر. الرجاء إرسال الرابط لتحميله.")

# دالة لعرض لوحة تحكم المالك
async def owner_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == OWNER_ID:
        keyboard = [
            [InlineKeyboardButton("إضافة قناة اشتراك إجباري", callback_data='add_channel')],
            [InlineKeyboardButton("حذف قناة اشتراك إجباري", callback_data='remove_channel')],
            [InlineKeyboardButton("إرسال إذاعة لجميع المستخدمين", callback_data='broadcast')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚙️ مرحبًا بك في لوحة التحكم الخاصة بالمالك. اختر إحدى الخيارات أدناه:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ أنت لست المالك!")

# إعداد البوت
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("owner", owner_control))  # إضافة لوحة التحكم للمالك
    application.add_handler(CommandHandler("add_channel", add_channel))  # إضافة قناة اشتراك
    application.add_handler(CommandHandler("remove_channel", remove_channel))  # حذف قناة اشتراك
    application.add_handler(CallbackQueryHandler(button_handler))  # إضافة معالجة الأزرار
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_user))  # إشعار عند دخول مستخدمين جدد

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
