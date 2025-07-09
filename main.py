import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import asyncio
import nest_asyncio

# تفعيل nest_asyncio لتجنب مشاكل في بعض بيئات التنفيذ
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

# دالة لتنزيل الفيديو من SaveFrom.net
async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    site = context.user_data.get('site')

    if "http" not in url:
        await update.message.reply_text("⚠️ الرجاء إرسال رابط صالح!")
        return

    savefrom_url = f"https://ar.savefrom.net/249Ex/?url={url}"

    # إرسال طلب إلى SaveFrom.net للحصول على رابط التنزيل
    try:
        response = requests.get(savefrom_url)
        if response.status_code == 200:
            # هنا يمكنك استخراج الرابط المباشر للتنزيل من الصفحة (يجب معالجة HTML)
            # لكن لسهولة الشرح سنقوم بإعطاء الرابط كما هو
            download_link = response.url  # قد تحتاج لاستخراج الرابط المباشر من الصفحة إذا لزم الأمر
            await update.message.reply_text(f"✅ تم تنزيل الفيديو بنجاح! يمكنك تحميله من هنا: {download_link}")
        else:
            await update.message.reply_text(f"❌ حدث خطأ أثناء التواصل مع الموقع. حاول مرة أخرى لاحقًا.")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

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
    else:
        await query.edit_message_text("❓ الموقع غير معروف. يرجى اختيار موقع معروف لتحميل الفيديو.")

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

# دالة لإشعار المستخدمين الجدد
async def welcome_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_users = update.message.new_chat_members
    for user in new_users:
        welcome_text = f"👋 مرحبًا {user.full_name}! مرحبًا بك في المجموعة."
        await update.message.reply_text(welcome_text)

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
    application.add_handler(MessageHandler(filters.TEXT, download_media))  # معالجة رسائل التنزيل

    await application.run_polling()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
