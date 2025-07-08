import telebot
from telebot import types
from pymongo import MongoClient
import time
import os

# ====== الإعدادات ======
TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 8011996271

REQUIRED_CHANNEL = "@YourChannelUsername"  # غيّر اسم القناة هنا

MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
    print("عيّن متغير البيئة MONGODB_URI في هيروكو مع رابط MongoDB.")
    exit(1)

client = MongoClient(MONGO_URI)
db = client['maria_bot_db']
groups_col = db['groups']

bot = telebot.TeleBot(TOKEN)

lock_types_map_ar = {
    "الصور": "photo",
    "الفيديو": "video",
    "الروابط": "links",
    "التوجيه": "forward",
    "الملصقات": "sticker",
    "الملفات": "document",
    "الصوتيات": "audio",
    "الصوت": "voice",
}

# ====== دوال الصلاحيات ======
def is_owner(user_id):
    return user_id == OWNER_ID

def is_group_owner(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

def is_bot_admin(chat_id, user_id):
    group = groups_col.find_one({"chat_id": chat_id})
    if not group:
        return False
    admins = group.get("admins", [])
    return user_id in admins

# ====== قواعد البيانات ======
def get_group(chat_id):
    group = groups_col.find_one({"chat_id": chat_id})
    if not group:
        group = {
            "chat_id": chat_id,
            "admins": [],
            "locks": {v: False for v in lock_types_map_ar.values()},
            "welcome": True,
            "group_subscription_required": True,
            "chat_locked": False,  # لقفل الدردشة نصيا
        }
        groups_col.insert_one(group)
    return group

def update_group(chat_id, data):
    groups_col.update_one({"chat_id": chat_id}, {"$set": data}, upsert=True)

# ====== الاشتراك الإجباري ======
def check_group_subscription(chat_id, user_id):
    group = get_group(chat_id)
    if not group.get("group_subscription_required", True):
        return True
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def require_subscription(func):
    def wrapper(message):
        if not check_group_subscription(message.chat.id, message.from_user.id):
            bot.reply_to(message, f"يجب الاشتراك في القناة {REQUIRED_CHANNEL} أولاً لاستخدام القروب.")
            return
        return func(message)
    return wrapper

# ====== أوامر الاشتراك الإجباري (مالك القروب) ======
@bot.message_handler(commands=["تفعيل_الاشتراك"])
def enable_subscription(message):
    if not is_group_owner(message.chat.id, message.from_user.id):
        bot.reply_to(message, "فقط مالك القروب يمكنه تفعيل الاشتراك الإجباري.")
        return
    update_group(message.chat.id, {"group_subscription_required": True})
    bot.reply_to(message, "تم تفعيل الاشتراك الإجباري في هذا القروب.")

@bot.message_handler(commands=["تعطيل_الاشتراك"])
def disable_subscription(message):
    if not is_group_owner(message.chat.id, message.from_user.id):
        bot.reply_to(message, "فقط مالك القروب يمكنه تعطيل الاشتراك الإجباري.")
        return
    update_group(message.chat.id, {"group_subscription_required": False})
    bot.reply_to(message, "تم تعطيل الاشتراك الإجباري في هذا القروب.")

# ====== زر التعليمات، تواصل، واضف البوت ======
@bot.message_handler(commands=["start"])
def start_handler(message):
    keyboard = types.InlineKeyboardMarkup()
    btn_help = types.InlineKeyboardButton("تعليمات", callback_data="show_help")
    btn_contact = types.InlineKeyboardButton("تواصل مع المطور", url="https://t.me/T_4IJ")
    bot_username = bot.get_me().username
    invite_url = f"https://t.me/{bot_username}?startgroup=true"
    btn_add_bot = types.InlineKeyboardButton("اضف البوت إلى مجموعتك", url=invite_url)
    keyboard.add(btn_help)
    keyboard.add(btn_contact)
    keyboard.add(btn_add_bot)

    bot.send_message(message.chat.id,
        "أهلاً بك في بوت ماريا للحماية المتطورة\n"
        "استخدم الأزرار أدناه للاطلاع على التعليمات أو التواصل مع المطور أو لإضافة البوت إلى مجموعتك.",
        reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "show_help")
def callback_show_help(call):
    help_text = (
        "قائمة أوامر البوت:\n\n"
        "مالك البوت:\n"
        "broadcast نص الإذاعة\n"
        "admin\n"
        "رفع_مشرف (بالرد على رسالة العضو)\n"
        "تنزيل_مشرف (بالرد)\n\n"
        "مالك القروب:\n"
        "تفعيل_الاشتراك\n"
        "تعطيل_الاشتراك\n"
        "كتم (بالرد)\n"
        "فك_كتم (بالرد)\n"
        "حظر (بالرد)\n"
        "الغاء_حظر (بالرد)\n"
        "قفل نوع (مثل: الصور، الروابط)\n"
        "فتح نوع\n"
        "تفعيل_الترحيب\n"
        "تعطيل_الترحيب\n"
        "قفل_الدردشة\n"
        "فتح_الدردشة\n\n"
        "ملاحظة: يجب الرد على العضو عند تنفيذ أوامر الحظر والكتم والمشرفين."
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, help_text)

# ====== أوامر عامة ======
@bot.message_handler(commands=["help"])
@require_subscription
def help_handler(message):
    text = (
        "أوامر البوت:\n\n"
        "مالك البوت:\n"
        "broadcast نص\n"
        "admin\n"
        "رفع_مشرف (بالرد على رسالة العضو)\n"
        "تنزيل_مشرف (بالرد)\n\n"
        "مالك القروب:\n"
        "تفعيل_الاشتراك\n"
        "تعطيل_الاشتراك\n"
        "كتم (بالرد)\n"
        "فك_كتم (بالرد)\n"
        "حظر (بالرد)\n"
        "الغاء_حظر (بالرد)\n"
        "قفل نوع\n"
        "فتح نوع\n"
        "تفعيل_الترحيب\n"
        "تعطيل_الترحيب\n"
        "قفل_الدردشة\n"
        "فتح_الدردشة\n"
    )
    bot.send_message(message.chat.id, text)

# ====== إدارة المشرفين (مالك البوت فقط) ======
def get_target_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "الرجاء الرد على رسالة العضو.")
        return None
    return message.reply_to_message.from_user

@bot.message_handler(commands=["رفع_مشرف"])
def promote_admin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "فقط مالك البوت يمكنه رفع مشرف.")
        return
    target = get_target_user(message)
    if not target:
        return
    group = get_group(message.chat.id)
    admins = group.get("admins", [])
    if target.id in admins:
        bot.reply_to(message, f"العضو {target.first_name} مشرف بالفعل.")
        return
    admins.append(target.id)
    update_group(message.chat.id, {"admins": admins})
    bot.reply_to(message, f"تم رفع {target.first_name} مشرف.")

@bot.message_handler(commands=["تنزيل_مشرف"])
def demote_admin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "فقط مالك البوت يمكنه تنزيل مشرف.")
        return
    target = get_target_user(message)
    if not target:
        return
    group = get_group(message.chat.id)
    admins = group.get("admins", [])
    if target.id not in admins:
        bot.reply_to(message, f"العضو {target.first_name} ليس مشرفاً.")
        return
    admins.remove(target.id)
    update_group(message.chat.id, {"admins": admins})
    bot.reply_to(message, f"تم تنزيل {target.first_name} من المشرفين.")

@bot.message_handler(commands=["admin"])
def show_admins(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "هذا الأمر خاص بمالك البوت فقط.")
        return
    all_groups = groups_col.find()
    text = ""
    for group in all_groups:
        chat_id = group["chat_id"]
        admins = group.get("admins", [])
        if not admins:
            continue
        text += f"قروب: {chat_id}\nالمشرفين:\n"
        for admin_id in admins:
            try:
                user = bot.get_chat_member(chat_id, admin_id).user
                name = user.first_name
                username = "@" + user.username if user.username else "لا يوجد"
            except Exception:
                name = "غير معروف"
                username = "غير معروف"
            text += f"- {name} ({username}) — {admin_id}\n"
        text += "\n"
    if not text:
        text = "لا يوجد مشرفين مسجلين."
    bot.send_message(message.chat.id, text)

# ====== إذاعة (مالك البوت فقط) ======
@bot.message_handler(commands=["broadcast"])
def broadcast_handler(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "هذا الأمر خاص بمالك البوت فقط.")
        return
    text = message.text.partition(" ")[2]
    if not text:
        bot.reply_to(message, "أرسل الأمر مع نص الإذاعة.")
        return
    all_groups = groups_col.find()
    success = 0
    failed = 0
    for group in all_groups:
        chat_id = group["chat_id"]
        try:
            bot.send_message(chat_id, f"إذاعة من المالك:\n\n{text}")
            success += 1
        except Exception:
            failed += 1
    bot.reply_to(message, f"تم إرسال الإذاعة إلى {success} قروب.\nفشل في {failed} قروب.")

# ====== أوامر الحماية ======
@bot.message_handler(commands=["كتم"])
def mute_user(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id) or is_bot_admin(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "ليس لديك صلاحية.")
        return
    target = get_target_user(message)
    if not target:
        return
    try:
        until_date = int(time.time()) + 60*60*24*7
        bot.restrict_chat_member(message.chat.id, target.id, can_send_messages=False, until_date=until_date)
        bot.reply_to(message, f"تم كتم {target.first_name} لمدة أسبوع.")
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")

@bot.message_handler(commands=["فك_كتم"])
def unmute_user(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id) or is_bot_admin(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "ليس لديك صلاحية.")
        return
    target = get_target_user(message)
    if not target:
        return
    try:
        bot.restrict_chat_member(message.chat.id, target.id, can_send_messages=True)
        bot.reply_to(message, f"تم فك كتم {target.first_name}.")
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")

@bot.message_handler(commands=["حظر"])
def ban_user(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id) or is_bot_admin(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "ليس لديك صلاحية.")
        return
    target = get_target_user(message)
    if not target:
        return
    try:
        bot.kick_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"تم طرد {target.first_name} من القروب.")
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")

@bot.message_handler(commands=["الغاء_حظر"])
def unban_user(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id) or is_bot_admin(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "ليس لديك صلاحية.")
        return
    target = get_target_user(message)
    if not target:
        return
    try:
        bot.unban_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"تم إلغاء حظر {target.first_name}.")
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")

# ====== قفل وفتح أنواع الرسائل ======
@bot.message_handler(commands=["قفل"])
def lock_type(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "فقط مالك القروب ومالك البوت يمكنهم قفل الأنواع.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "أرسل نوع القفل بعد الأمر، مثل:\nقفل الصور")
        return
    lock_name_ar = args[1].strip()
    if lock_name_ar not in lock_types_map_ar:
        bot.reply_to(message, "نوع القفل غير معروف. الأنواع المتاحة:\n" + ", ".join(lock_types_map_ar.keys()))
        return
    lock_key = lock_types_map_ar[lock_name_ar]
    group = get_group(message.chat.id)
    locks = group.get("locks", {})
    locks[lock_key] = True
    update_group(message.chat.id, {"locks": locks})
    bot.reply_to(message, f"تم قفل {lock_name_ar} في القروب.")

@bot.message_handler(commands=["فتح"])
def unlock_type(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "فقط مالك القروب ومالك البوت يمكنهم فتح الأنواع.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "أرسل نوع الفتح بعد الأمر، مثل:\nفتح الصور")
        return
    lock_name_ar = args[1].strip()
    if lock_name_ar not in lock_types_map_ar:
        bot.reply_to(message, "نوع الفتح غير معروف. الأنواع المتاحة:\n" + ", ".join(lock_types_map_ar.keys()))
        return
    lock_key = lock_types_map_ar[lock_name_ar]
    group = get_group(message.chat.id)
    locks = group.get("locks", {})
    locks[lock_key] = False
    update_group(message.chat.id, {"locks": locks})
    bot.reply_to(message, f"تم فتح {lock_name_ar} في القروب.")

# ====== أوامر قفل وفتح الدردشة النصية ======
@bot.message_handler(commands=["قفل_الدردشة"])
def lock_chat(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "فقط مالك القروب ومالك البوت يمكنهم قفل الدردشة.")
        return
    group = get_group(message.chat.id)
    update_group(message.chat.id, {"chat_locked": True})
    # تقييد إرسال الرسائل النصية للجميع إلا الأدمن والمالك
    bot.set_chat_permissions(message.chat.id, types.ChatPermissions(can_send_messages=False))
    bot.reply_to(message, "تم قفل الدردشة النصية في القروب.")

@bot.message_handler(commands=["فتح_الدردشة"])
def unlock_chat(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "فقط مالك القروب ومالك البوت يمكنهم فتح الدردشة.")
        return
    group = get_group(message.chat.id)
    update_group(message.chat.id, {"chat_locked": False})
    # السماح للجميع بإرسال الرسائل
    bot.set_chat_permissions(message.chat.id, types.ChatPermissions(can_send_messages=True,
                                                                   can_send_media_messages=True,
                                                                   can_send_other_messages=True,
                                                                   can_add_web_page_previews=True))
    bot.reply_to(message, "تم فتح الدردشة النصية في القروب.")

# ====== الترحيب ======
@bot.message_handler(commands=["تفعيل_الترحيب"])
def enable_welcome(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "فقط مالك القروب ومالك البوت يمكنهم تفعيل الترحيب.")
        return
    update_group(message.chat.id, {"welcome": True})
    bot.reply_to(message, "تم تفعيل الترحيب في القروب.")

@bot.message_handler(commands=["تعطيل_الترحيب"])
def disable_welcome(message):
    if not (is_owner(message.from_user.id) or is_group_owner(message.chat.id, message.from_user.id)):
        bot.reply_to(message, "فقط مالك القروب ومالك البوت يمكنهم تعطيل الترحيب.")
        return
    update_group(message.chat.id, {"welcome": False})
    bot.reply_to(message, "تم تعطيل الترحيب في القروب.")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_members(message):
    group = get_group(message.chat.id)
    if not group.get("welcome", True):
        return
    for new_member in message.new_chat_members:
        if new_member.is_bot:
    continue
