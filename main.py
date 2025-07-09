import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# إعداد تسجيل الدخول
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# معرف المالك (يمكنك تعديل هذا بالـ user ID الخاص بالمالك)
OWNER_ID = 1310488710  # ضع هنا معرف المالك

# قناة الاشتراك الإجباري
mandatory_channel = None  # لا توجد قناة بشكل افتراضي
notify_new_users = True  # إشعار دخول المستخدمين الجدد مفعل بشكل افتراضي

# قائمة لتخزين معرفات المستخدمين
user_ids = set()

# دالة لعرض الأزرار للمستخدم
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تحقق من الاشتراك الإجباري
    if mandatory_channel:
        # تحقق من اشتراك المستخدم في القناة
        member = await update.bot.get_chat_member(mandatory_channel, update.message.from_user.id)
        if member.status not in ['member', 'administrator']:
            await update.message.reply_text(f"⚠️ يجب عليك الاشتراك في القناة: {mandatory_channel}\nيمكنك الاشتراك عبر هذا الرابط: https://t.me/{mandatory_channel[1:]}")
            return

    # إضافة معرف المستخدم إلى القائمة
    user_ids.add(update.message.from_user.id)

    # الرسالة الترحيبية مع وصف مختصر للبوت مع الإيموجيات
    welcome_message = (
        "👋 مرحبًا! أنا بوت لتحميل الفيديوهات 🎥\n\n"
        "اختر الموقع الذي تريد تنزيل الفيديو منه 💻👇\n\n"
        "إذا كنت بحاجة إلى المساعدة، تواصل مع المطور عبر الزر أدناه 👨‍💻"
    )
    
    # الأزرار
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

# دالة خاصة لزر /admin للمالك
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == OWNER_ID:  # تحقق إذا كان المرسل هو المالك فقط
        keyboard = [
            [InlineKeyboardButton("إدارة البوت", callback_data='manage_bot')],
            [InlineKeyboardButton("عرض الإحصائيات", callback_data='view_stats')],
            [InlineKeyboardButton("إضافة قناة اشتراك إجباري", callback_data='add_channel')],
            [InlineKeyboardButton("حذف قناة اشتراك إجباري", callback_data='remove_channel')],
            [InlineKeyboardButton("إرسال إذاعة لجميع المستخدمين", callback_data='broadcast')],
            [InlineKeyboardButton("تشغيل إشعار دخول المستخدمين" if not notify_new_users else "إيقاف إشعار دخول المستخدمين", callback_data='toggle_notifications')],
            [InlineKeyboardButton("تواصل مع المطور 📨", url="https://t.me/T_4IJ")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚙️ مرحبًا بك في لوحة التحكم الخاصة بالمالك. اختر إحدى الخيارات أدناه:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ أنت لست المالك!")

# دالة لإضافة قناة اشتراك إجباري
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == OWNER_ID:
        # حفظ القناة الجديدة التي سيتم اشتراك المستخدم فيها
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

# دالة لإرسال رسالة إذاعة لجميع المستخدمين
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == OWNER_ID:
        # النص الذي سيتم إرساله في الإذاعة
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

# دالة لتفعيل أو إيقاف إشعار دخول المستخدمين الجدد
async def toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global notify_new_users
    if update.message.from_user.id == OWNER_ID:
        notify_new_users = not notify_new_users  # التبديل بين التشغيل والإيقاف
        status = "تشغيل" if notify_new_users else "إيقاف"
        await update.message.reply_text(f"✅ تم {status} إشعار دخول المستخدمين الجدد.")
    else:
        await update.message.reply_text("❌ أنت لست المالك!")

# دالة للإشعار عند دخول المستخدمين الجدد
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

    # إعدادات yt-dlp العامة
    ydl_opts = {
        'format': 'best',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
    }

    # تخصيص الإعدادات للموقع المختار
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
            # محاولة تحميل الفيديو
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)

            await update.message.reply_text(f"✅ تم تنزيل الفيديو من {site.capitalize()} بنجاح: {video_filename}")

            # إرسال الفيديو أو الصوت للمستخدم
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

    if data == 'toggle_notifications':
        # تبديل حالة الإشعارات
        global notify_new_users
        notify_new_users = not notify_new_users
        status = "تشغيل" if notify_new_users else "إيقاف"
        await query.edit_message_text(f"✅ تم {status} إشعار دخول المستخدمين الجدد.")
    
    elif data == 'youtube':
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

# إعداد البوت
async def main():
    # قم بتغيير التوكن الخاص بك هنا
    application = ApplicationBuilder().token("6477545499:AAHkCgwT5Sn1otiMst_sAOmoAp_QC1_ILzA").build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))  # إضافة الأمر /admin للمالك
    application.add_handler(CommandHandler("add_channel", add_channel))  # إضافة قناة اشتراك
    application.add_handler(CommandHandler("remove_channel", remove_channel))  # حذف قناة اشتراك
    application.add_handler(CommandHandler("broadcast", broadcast_message))  # إرسال رسالة إذاعة
    application.add_handler(CallbackQueryHandler(button_handler))  # إضافة معالجة الأزرار
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_user))  # إشعار عند دخول مستخدمين جدد

    # بدء البوت
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())  # لا حاجة لتغيير هذا في حالتك
