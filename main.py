import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import yt_dlp

# تعيين API ID و API Hash و Bot Token بشكل ثابت داخل الكود
api_id = 10045162  # استبدل هذا بـ API ID الخاص بك
api_hash = "5b58442987a667be5f6a521f7de4a961"  # استبدل هذا بـ API Hash الخاص بك
bot_token = "7362214073:AAHfJS5mh7O2xDPTvfVKU3ix35prCeZxgfc"  # استبدل هذا بـ Bot Token الخاص بك

# إعداد البوت باستخدام Pyrogram
app = Client("video_downloader_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# قائمة المديرين المسموح لهم بالتحكم
admins = [8011996271]  # ضع هنا ID المديرين

# تأكد من أن مجلد downloads موجود
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# وظيفة لتحميل الفيديو باستخدام yt-dlp
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # حفظ الفيديو في مجلد downloads
        'quiet': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)  # تنزيل الفيديو
    return info

# دالة لإرسال الأزرار الخاصة بالمالكين
def get_admin_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("عرض الفيديوهات المحملة", callback_data="show_downloads")],
        [InlineKeyboardButton("حذف الفيديوهات", callback_data="delete_downloads")],
        [InlineKeyboardButton("إيقاف تحميل من يوتيوب", callback_data="disable_youtube")],
        [InlineKeyboardButton("إيقاف تحميل من إنستجرام", callback_data="disable_instagram")],
        [InlineKeyboardButton("إعدادات البوت", callback_data="bot_settings")],
        [InlineKeyboardButton("إضافة قناة اشتراك جباري", callback_data="add_channel")],
        [InlineKeyboardButton("حذف قناة اشتراك جباري", callback_data="remove_channel")],
        [InlineKeyboardButton("حظر عضو", callback_data="ban_user")],
        [InlineKeyboardButton("مساعدة", callback_data="help")],
    ])

# دالة لإرسال الأزرار الخاصة بالزوار
def get_visitor_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("تحميل من يوتيوب", callback_data="download_youtube")],
        [InlineKeyboardButton("تحميل من إنستجرام", callback_data="download_instagram")],
        [InlineKeyboardButton("تحميل من تويتر", callback_data="download_twitter")],
        [InlineKeyboardButton("تحميل من سناب شات", callback_data="download_snapchat")],
        [InlineKeyboardButton("تحميل من فيسبوك", callback_data="download_facebook")],
        [InlineKeyboardButton("تحميل من تيك توك", callback_data="download_tiktok")],
        [InlineKeyboardButton("مساعدة", callback_data="help")],
    ])

# دالة للتحقق من كون المستخدم مدير
def is_admin(user_id):
    return user_id in admins

# دالة للتحقق من اشتراك المستخدم في القنوات المطلوبة
async def check_subscription(user_id):
    for channel in required_channels:
        try:
            chat_member = await app.get_chat_member(channel, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            return False
    return True

# رد على بدء المحادثة مع البوت (رسالة الترحيب)
@app.on_message(filters.command("start"))
async def start(client, message):
    user_first_name = message.from_user.first_name
    await message.reply(f"مرحبًا {user_first_name}، أنا بوت تنزيل الفيديوهات! اختر الفيديو الذي ترغب في تنزيله من خلال الأزرار أدناه.", reply_markup=get_visitor_buttons())

# الرد على رسالة تحتوي على رابط
@app.on_message(filters.text)
async def handle_message(client, message):
    if message.text.startswith("http"):
        # التحقق من الاشتراك في القنوات الجباريّة
        if await check_subscription(message.from_user.id):
            try:
                video_url = message.text
                video_info = download_video(video_url)

                # إرسال الفيديو للمستخدم بعد التنزيل
                if os.path.exists(f"downloads/{video_info['title']}.mp4"):
                    await message.reply_video(f"downloads/{video_info['title']}.mp4")
                else:
                    await message.reply("حدث خطأ أثناء تنزيل الفيديو.")
                
                # تحديد الأزرار بناءً على المستخدم (مالك أو زائر)
                if is_admin(message.from_user.id):
                    await message.reply("تم تنزيل الفيديو بنجاح.", reply_markup=get_admin_buttons())
                else:
                    await message.reply("تم تنزيل الفيديو بنجاح.", reply_markup=get_visitor_buttons())

            except Exception as e:
                await message.reply(f"حدث خطأ: {e}")
        else:
            await message.reply("أنت بحاجة للاشتراك في القنوات المطلوبة لاستخدام البوت.")

# الرد على الأوامر الخاصة بالمدير
@app.on_callback_query(filters.regex("add_channel"))
async def add_channel(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return

    await callback_query.answer("يرجى إرسال رابط القناة التي تريد إضافتها.")

@app.on_message(filters.text)
async def handle_add_channel(message):
    if message.text.startswith("https://t.me/"):
        required_channels.append(message.text)
        await message.reply(f"تم إضافة القناة {message.text} إلى القنوات الجبارة.")
    else:
        await message.reply("يرجى إرسال رابط صحيح للقناة.")

@app.on_callback_query(filters.regex("remove_channel"))
async def remove_channel(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return

    await callback_query.answer("يرجى إرسال رابط القناة التي تريد حذفها.")

@app.on_message(filters.text)
async def handle_remove_channel(message):
    if message.text in required_channels:
        required_channels.remove(message.text)
        await message.reply(f"تم حذف القناة {message.text} من القنوات الجبارة.")
    else:
        await message.reply("هذه القناة غير موجودة في القائمة.")

@app.on_callback_query(filters.regex("ban_user"))
async def ban_user(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return

    await callback_query.answer("يرجى إرسال ID العضو الذي تريد حظره.")

@app.on_message(filters.text)
async def handle_ban_user(message):
    try:
        user_id = int(message.text)
        if user_id not in banned_users:
            banned_users.append(user_id)
            await message.reply(f"تم حظر العضو {user_id}.")
        else:
            await message.reply(f"العضو {user_id} محظور بالفعل.")
    except ValueError:
        await message.reply("يرجى إرسال ID صالح للعضو.")

@app.on_callback_query(filters.regex("show_downloads"))
async def show_downloads(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return
    
    video_files = os.listdir("downloads/")
    if video_files:
        videos = "\n".join(video_files)
        await callback_query.edit_message_text(f"الفيديوهات المحملة:\n{videos}")
    else:
        await callback_query.edit_message_text("لا توجد فيديوهات محملة حاليًا.")

@app.on_callback_query(filters.regex("delete_downloads"))
async def delete_downloads(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return
    
    video_files = os.listdir("downloads/")
    if video_files:
        for video in video_files:
            os.remove(f"downloads/{video}")
        await callback_query.edit_message_text("تم حذف جميع الفيديوهات.")
    else:
        await callback_query.edit_message_text("لا توجد فيديوهات لحذفها.")

@app.on_callback_query(filters.regex("disable_youtube"))
async def disable_youtube(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return
    
    await callback_query.edit_message_text("تم إيقاف تحميل الفيديوهات من يوتيوب.")

@app.on_callback_query(filters.regex("disable_instagram"))
async def disable_instagram(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return
    
    await callback_query.edit_message_text("تم إيقاف تحميل الفيديوهات من إنستجرام.")

@app.on_callback_query(filters.regex("bot_settings"))
async def bot_settings(client, callback_query):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("أنت لا تملك صلاحيات للوصول إلى هذه الميزة!")
        return
    
    await callback_query.edit_message_text("إعدادات البوت: يمكنك تعديل إعدادات التحميل، اللغة، وأذونات أخرى.")

@app.on_callback_query(filters.regex("help"))
async def help(client, callback_query):
    help_message = """
    استخدم الأزرار لاختيار المصدر الذي تريد تحميل الفيديو منه.
    يمكنك التحكم في إعدادات البوت من خلال لوحة التحكم الخاصة بالمدير:
    - عرض الفيديوهات المحملة
    - حذف الفيديوهات المحملة
    - حظر الأعضاء
    """
    await callback_query.edit_message_text(help_message)

# إشعار عند دخول عضو جديد
@app.on_chat_member_updated()
async def new_member(client, message):
    if message.new_chat_member:
        # إشعار المالك عند دخول عضو جديد
        for admin in admins:
            user = await app.get_users(admin)
            await app.send_message(user.id, f"أهلاً بالعضو الجديد: {message.new_chat_member.user.first_name}")

# تشغيل البوت
app.run()
