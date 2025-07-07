# ─── Maria Bot v2.1 ───
import telebot
from telebot import types
import json, os, threading, time

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
OWNER_ID = 1310488710
DEFAULT_CHANNEL = "T_4IJ"

bot = telebot.TeleBot(TOKEN)
os.makedirs("data", exist_ok=True)

def jload(path, default):
    if not os.path.exists(path):
        jdump(path, default)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def jdump(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

settings = jload("data/settings.json", {"sub_channel": DEFAULT_CHANNEL})
users = jload("data/users.json", {})
banned = jload("data/banned.json", [])
warns = jload("data/warns.json", {})
logs = jload("data/logs.json", [])  # سجل الإدارة

def save_all():
    jdump("data/settings.json", settings)
    jdump("data/users.json", users)
    jdump("data/banned.json", banned)
    jdump("data/warns.json", warns)
    jdump("data/logs.json", logs)

def log_event(event):
    logs.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {event}")
    if len(logs) > 500:
        logs.pop(0)  # تخزين حتى 500 سجل
    save_all()

def is_admin(uid):
    return uid == OWNER_ID

def check_sub(uid):
    try:
        chat = bot.get_chat_member(f"@{settings['sub_channel']}", uid)
        return chat.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error in check_sub: {e}")
        return False

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    if str(uid) not in users:
        users[str(uid)] = {"warns": 0}
        save_all()
    if uid in banned:
        return bot.reply_to(message, "🚫 أنت محظور من استخدام البوت.")
    if not is_admin(uid) and not check_sub(uid):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{settings['sub_channel']}"))
        kb.add(types.InlineKeyboardButton("✅ تحقّق", callback_data="verify_sub"))
        return bot.send_message(message.chat.id, "⚠️ يجب الاشتراك في القناة لاستخدام البوت.", reply_markup=kb)
    if is_admin(uid):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🛠️ لوحة تحكم", callback_data="admin_panel"))
        bot.send_message(message.chat.id, "👑 مرحباً بك أيها المدير. اختر من لوحة التحكم 👇", reply_markup=kb)
        log_event(f"المالك {message.from_user.first_name} دخل البوت (ID:{uid})")
        return
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت ماريا! أرسل /help لعرض الأوامر.")
    # إشعار المالك بدخول مستخدم جديد
    try:
        bot.send_message(OWNER_ID, f"👤 مستخدم جديد دخل البوت:\nID: {uid}\nName: {message.from_user.first_name}")
    except Exception as e:
        print(f"Error sending new user notification: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "verify_sub")
def verify_sub(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق بنجاح!")
        bot.send_message(call.message.chat.id, "🎉 شكراً لاشتراكك بالقناة!")
    else:
        bot.answer_callback_query(call.id, "🚫 ما زلت غير مشترك.")

@bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
def admin_panel(call):
    if not is_admin(call.from_user.id): return
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📢 قناة الاشتراك", callback_data="set_channel"),
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"),
        types.InlineKeyboardButton("🚫 قائمة الحظر", callback_data="ban_list"),
        types.InlineKeyboardButton("📨 بث رسالة", callback_data="broadcast"),
        types.InlineKeyboardButton("📜 سجل الإدارة", callback_data="show_logs")
    )
    bot.send_message(call.message.chat.id, "🛠️ اختر إجراء من لوحة التحكم:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "set_channel")
def set_channel(call):
    if not is_admin(call.from_user.id): return
    msg = bot.send_message(call.message.chat.id, "📢 أرسل معرف القناة الجديدة بدون @:")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(message):
    settings["sub_channel"] = message.text.strip().replace("@", "")
    save_all()
    bot.reply_to(message, f"✅ تم حفظ قناة الاشتراك: {settings['sub_channel']}")
    log_event(f"المالك غيّر قناة الاشتراك إلى: {settings['sub_channel']}")

@bot.callback_query_handler(func=lambda c: c.data == "stats")
def stats(call):
    if not is_admin(call.from_user.id): return
    text = (
        f"👥 عدد المستخدمين: {len(users)}\n"
        f"🚫 عدد المحظورين: {len(banned)}\n"
        f"⚠️ التحذيرات المسجلة: {len(warns)}"
    )
    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda c: c.data == "ban_list")
def ban_list(call):
    if not is_admin(call.from_user.id): return
    if not banned:
        bot.send_message(call.message.chat.id, "🚫 قائمة الحظر فارغة.")
        return
    text = "🚫 قائمة المستخدمين المحظورين:\n"
    for user_id in banned:
        text += f"- {user_id}\n"
    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda c: c.data == "broadcast")
def ask_broadcast(call):
    if not is_admin(call.from_user.id): return
    msg = bot.send_message(call.message.chat.id, "📝 أرسل الرسالة التي تريد بثها:")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(msg):
    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(uid, msg.text)
            sent += 1
        except Exception as e:
            failed += 1
            print(f"Broadcast error sending to {uid}: {e}")
    bot.reply_to(msg, f"✅ تم الإرسال إلى {sent} مستخدم، فشل {failed}.")
    log_event(f"المالك بث رسالة: {msg.text}")

@bot.callback_query_handler(func=lambda c: c.data == "show_logs")
def show_logs(call):
    if not is_admin(call.from_user.id): return
    logs_text = "\n".join(logs[-20:]) if logs else "لا توجد سجلات بعد."
    bot.send_message(call.message.chat.id, f"📜 آخر 20 حدث:\n{logs_text}")

@bot.message_handler(commands=["ban"])
def ban_user(msg):
    if not is_admin(msg.from_user.id) or not msg.reply_to_message: return
    target = msg.reply_to_message.from_user.id
    if target not in banned:
        banned.append(target)
        save_all()
        bot.reply_to(msg, f"🚫 تم حظر المستخدم: {target}")
        log_event(f"المالك حظر المستخدم: {target}")

@bot.message_handler(commands=["unban"])
def unban_user(msg):
    if not is_admin(msg.from_user.id) or not msg.reply_to_message: return
    target = msg.reply_to_message.from_user.id
    if target in banned:
        banned.remove(target)
        save_all()
        bot.reply_to(msg, f"✅ تم رفع الحظر عن: {target}")
        log_event(f"المالك رفع الحظر عن المستخدم: {target}")

@bot.message_handler(commands=["warn"])
def warn_user(msg):
    if not msg.reply_to_message: return
    uid = str(msg.reply_to_message.from_user.id)
    warns[uid] = warns.get(uid, 0) + 1
    save_all()
    bot.reply_to(msg, f"⚠️ تحذير رقم {warns[uid]}")
    log_event(f"تم تحذير المستخدم {uid}، تحذير رقم {warns[uid]}")

    # كتم تلقائي بعد تحذيرين مع فك كتم بعد 5 دقائق
    if warns[uid] == 2:
        try:
            bot.restrict_chat_member(msg.chat.id, int(uid), types.ChatPermissions(can_send_messages=False))
            bot.send_message(msg.chat.id, f"🔇 تم كتم المستخدم {uid} بعد تحذيرين لمدة 5 دقائق.")
            log_event(f"المستخدم {uid} تم كتمه لمدة 5 دقائق بعد تحذيرين.")
            # بدء مؤقت لفك الكتم
            threading.Thread(target=auto_unmute, args=(msg.chat.id, int(uid), 300)).start()
        except Exception as e:
            print(f"Mute error: {e}")

    # حظر تلقائي بعد 3 تحذيرات
    if warns[uid] >= 3:
        if int(uid) not in banned:
            banned.append(int(uid))
            save_all()
            bot.send_message(msg.chat.id, f"🚫 تم حظر المستخدم بعد 3 تحذيرات.")
            log_event(f"المستخدم {uid} تم حظره بعد 3 تحذيرات.")

def auto_unmute(chat_id, user_id, delay_seconds):
    time.sleep(delay_seconds)
    try:
        bot.restrict_chat_member(chat_id, user_id, types.ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        ))
        bot.send_message(chat_id, f"🔊 تم فك كتم المستخدم {user_id} بعد انتهاء المدة.")
        log_event(f"المستخدم {user_id} تم فك كتمه تلقائياً بعد انتهاء مدة الكتم.")
    except Exception as e:
        print(f"Unmute error: {e}")

# حماية من الروابط في المجموعات
@bot.message_handler(content_types=['text'])
def protect_links(msg):
    if msg.text and ('http://' in msg.text or 'https://' in msg.text):
        if msg.chat.type in ['group', 'supergroup'] and not is_admin(msg.from_user.id):
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.send_message(msg.chat.id, f"🚫 الروابط ممنوعة يا {msg.from_user.first_name}!")
            except Exception as e:
                print(f"Delete message error (links): {e}")

# فلتر كلمات ممنوعة
bad_words = ["كلب", "حيوان", "تافه", "سخيف", "غبي"]
@bot.message_handler(content_types=['text'])
def filter_bad_words(msg):
    if msg.chat.type in ['group', 'supergroup'] and not is_admin(msg.from_user.id):
        if msg.text:
            for word in bad_words:
                if word in msg.text.lower():
                    try:
                        bot.delete_message(msg.chat.id, msg.message_id)
                        bot.send_message(msg.chat.id, f"🚫 لا تستخدم كلمات غير لائقة يا {msg.from_user.first_name}!")
                        return
                    except Exception as e:
                        print(f"Delete message error (bad words): {e}")

@bot.message_handler(commands=["help"])
def help_user(msg):
    text = (
        "📜 أوامر المستخدم:\n"
        "/help - عرض الأوامر\n\n"
        "👮‍♂️ أوامر الإدارة:\n"
        "/warn - تحذير (رد على رسالة)\n"
        "/ban - حظر (رد على رسالة)\n"
        "/unban - رفع حظر (رد على رسالة)\n"
        "/broadcast - بث\n"
        "/stats - إحصائيات\n"
        "/setsub - تعيين قناة الاشتراك"
    )
    bot.reply_to(msg, text)

# دعم أمر /setsub لتغيير قناة الاشتراك مباشرة
@bot.message_handler(commands=["setsub"])
def cmd_setsub(msg):
    if not is_admin(msg.from_user.id): return
    args = msg.text.split()
    if len(args) != 2:
        return bot.reply_to(msg, "❌ الرجاء إرسال المعرف الصحيح مع الأمر. مثال:\n/setsub T_4IJ")
    new_channel = args[1].strip().replace("@", "")
    settings["sub_channel"] = new_channel
    save_all()
    bot.reply_to(msg, f"✅ تم تعيين قناة الاشتراك إلى: {new_channel}")
    log_event(f"المالك غيّر قناة الاشتراك عبر الأمر إلى: {new_channel}")

print("🚀 Bot is running...")
bot.infinity_polling()
