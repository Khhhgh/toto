import telebot
from telebot import types
import json, os, time
from datetime import datetime

TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
ADMIN_IDS = [1310488710]

bot = telebot.TeleBot(TOKEN)
FILES = {
    "admins": "admins.json",
    "users": "users.json",
    "welcome": "welcome.json",
    "autoreplies": "autoreplies.json",
    "filters": "filters.json",
    "bans": "bans.json",
    "mutes": "mutes.json",
    "warnings": "warnings.json",
    "logs": "logs.json",
    "stats": "stats.json"
}
cache = {}

def load_data(file):
    if file in cache:
        return cache[file]
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        cache[file] = data
        return data

def save_data(file, data):
    cache[file] = data
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

for f in FILES.values():
    if not os.path.exists(f):
        save_data(f, {})

def is_admin(uid):
    admins = load_data(FILES["admins"])
    return uid in ADMIN_IDS or str(uid) in admins

def build_admins_keyboard():
    admins = load_data(FILES["admins"])
    kb = types.InlineKeyboardMarkup()
    for uid, name in admins.items():
        kb.add(types.InlineKeyboardButton(f"❌ {name}", callback_data=f"deladmin:{uid}"))
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, f"مرحباً {message.from_user.first_name}! اكتب 'القائمة' لعرض الأوامر.")

@bot.message_handler(func=lambda m: m.text=="القائمة" and is_admin(m.from_user.id))
def send_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("رفع ادمن", "خفض ادمن", "قائمة الأدمن")
    markup.add("حظر مؤقت", "فك الحظر", "كتم", "كتم مؤقت", "فك الكتم")
    markup.add("سجل المستخدم", "قائمة المحظورين", "تفعيل الفلاتر", "تعطيل الفلاتر")
    markup.add("تحديث الترحيب", "قائمة الردود التلقائية")
    markup.add("إضافة رد تلقائي", "حذف رد تلقائي", "عرض التحذيرات", "تحذير مستخدم", "عدد المستخدمين", "ارسال جماعي")
    bot.send_message(message.chat.id, "📋 قائمة الأوامر:", reply_markup=markup)

@bot.message_handler(commands=["الادمن"])
def cmd_admins(message):
    if not is_admin(message.from_user.id):
        return
    kb = build_admins_keyboard()
    if kb.inline_keyboard:
        bot.send_message(message.chat.id, "قائمة الأدمن (اضغط لحذف):", reply_markup=kb)
    else:
        bot.send_message(message.chat.id, "🚫 لا يوجد أدمن حاليا")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("deladmin:"))
def del_admin_callback(call):
    uid = call.data.split(":")[1]
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مسموح لك.")
        return
    admins = load_data(FILES["admins"])
    if uid in admins:
        name = admins.pop(uid)
        save_data(FILES["admins"], admins)
        bot.answer_callback_query(call.id, f"تم حذف {name} من الأدمن")
        kb = build_admins_keyboard()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
    else:
        bot.answer_callback_query(call.id, "هذا الأدمن غير موجود")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("رفع ادمن") and m.reply_to_message and is_admin(m.from_user.id))
def promote_admin(message):
    admins = load_data(FILES["admins"])
    uid = str(message.reply_to_message.from_user.id)
    admins[uid] = message.reply_to_message.from_user.first_name
    save_data(FILES["admins"], admins)
    bot.reply_to(message, f"✅ تم رفع {admins[uid]} كأدمن")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("خفض ادمن") and m.reply_to_message and is_admin(m.from_user.id))
def demote_admin(message):
    admins = load_data(FILES["admins"])
    uid = str(message.reply_to_message.from_user.id)
    if uid in admins:
        admins.pop(uid)
        save_data(FILES["admins"], admins)
        bot.reply_to(message, "✅ تم خفض المستخدم من الأدمن")
    else:
        bot.reply_to(message, "❌ هذا المستخدم ليس أدمن")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("حظر مؤقت") and m.reply_to_message and is_admin(m.from_user.id))
def temp_ban(message):
    parts = message.text.split()
    if len(parts)==3:
        try:
            minutes = int(parts[2])
            uid = str(message.reply_to_message.from_user.id)
            bans = load_data(FILES["bans"])
            bans[uid] = time.time() + minutes*60
            save_data(FILES["bans"], bans)
            bot.reply_to(message, f"⏳ تم حظر المستخدم مؤقتا لمدة {minutes} دقيقة")
        except:
            bot.reply_to(message, "❌ صيغة خاطئة. مثال: حظر مؤقت 10")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("فك الحظر") and m.reply_to_message and is_admin(m.from_user.id))
def unban_temp(message):
    uid = str(message.reply_to_message.from_user.id)
    bans = load_data(FILES["bans"])
    if uid in bans:
        bans.pop(uid)
        save_data(FILES["bans"], bans)
        bot.reply_to(message, "✅ تم فك الحظر")
    else:
        bot.reply_to(message, "❌ المستخدم غير محظور")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("كتم مؤقت") and m.reply_to_message and is_admin(m.from_user.id))
def mute_temp(message):
    parts = message.text.split()
    if len(parts) == 3:
        try:
            mins = int(parts[2])
            uid = str(message.reply_to_message.from_user.id)
            mutes = load_data(FILES["mutes"])
            until = time.time() + mins * 60
            mutes[uid] = until
            save_data(FILES["mutes"], mutes)
            bot.reply_to(message, f"🔇 تم كتم المستخدم مؤقتًا لـ {mins} دقيقة")
        except:
            bot.reply_to(message, "❌ صيغة خاطئة. مثال: كتم مؤقت 10")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("كتم") and m.reply_to_message and is_admin(m.from_user.id))
def mute_user(message):
    uid = str(message.reply_to_message.from_user.id)
    mutes = load_data(FILES["mutes"])
    mutes[uid] = True
    save_data(FILES["mutes"], mutes)
    bot.reply_to(message, "🔇 تم كتم المستخدم")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("فك الكتم") and m.reply_to_message and is_admin(m.from_user.id))
def unmute_user(message):
    uid = str(message.reply_to_message.from_user.id)
    mutes = load_data(FILES["mutes"])
    if uid in mutes:
        mutes.pop(uid)
        save_data(FILES["mutes"], mutes)
        bot.reply_to(message, "✅ تم فك الكتم")
    else:
        bot.reply_to(message, "❌ المستخدم غير مكتوم")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("سجل المستخدم") and m.reply_to_message and is_admin(m.from_user.id))
def user_logs(message):
    uid = str(message.reply_to_message.from_user.id)
    logs = load_data(FILES["logs"])
    history = logs.get(uid, [])[-20:]
    if history:
        out = '\n'.join(f"{log['time']}: {log['text']}" for log in history)
        bot.reply_to(message, out)
    else:
        bot.reply_to(message, "🚫 لا يوجد سجل")

@bot.message_handler(func=lambda m: m.text=="قائمة المحظورين" and is_admin(m.from_user.id))
def banned_list(message):
    bans = load_data(FILES["bans"])
    bot.reply_to(message, f"🚫 عدد المحظورين: {len(bans)}")

@bot.message_handler(func=lambda m: m.text=="تفعيل الفلاتر" and is_admin(m.from_user.id))
def enable_filters(message):
    filters = load_data(FILES["filters"])
    filters["enabled"] = True
    save_data(FILES["filters"], filters)
    bot.reply_to(message, "✅ تم تفعيل الفلاتر")

@bot.message_handler(func=lambda m: m.text=="تعطيل الفلاتر" and is_admin(m.from_user.id))
def disable_filters(message):
    filters = load_data(FILES["filters"])
    filters["enabled"] = False
    save_data(FILES["filters"], filters)
    bot.reply_to(message, "🛑 تم تعطيل الفلاتر")

@bot.message_handler(func=lambda m: m.text=="تحديث الترحيب" and is_admin(m.from_user.id))
def update_welcome(message):
    msg = bot.send_message(message.chat.id, "✏️ ارسل رسالة الترحيب (يمكنك استخدام {name} لاسم المستخدم)")
    bot.register_next_step_handler(msg, set_welcome_message)

def set_welcome_message(message):
    welcome = load_data(FILES["welcome"])
    welcome[str(message.chat.id)] = message.text
    save_data(FILES["welcome"], welcome)
    bot.reply_to(message, "✅ تم حفظ رسالة الترحيب")

@bot.message_handler(func=lambda m: m.text=="قائمة الردود التلقائية" and is_admin(m.from_user.id))
def show_autoreplies(message):
    autoreplies = load_data(FILES["autoreplies"])
    if autoreplies:
        text = "📜 الردود التلقائية:"
        kb = types.InlineKeyboardMarkup()
        for k,v in autoreplies.items():
            text += f"\n- {k} → {v}"
            kb.add(types.InlineKeyboardButton(f"حذف {k}", callback_data=f"delautoreply:{k}"))
        bot.send_message(message.chat.id, text, reply_markup=kb)
    else:
        bot.reply_to(message, "🚫 لا توجد ردود تلقائية")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("delautoreply:"))
def del_autoreply_cb(call):
    key = call.data.split(":",1)[1]
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مسموح لك.")
        return
    autoreplies = load_data(FILES["autoreplies"])
    if key in autoreplies:
        autoreplies.pop(key)
        save_data(FILES["autoreplies"], autoreplies)
        bot.answer_callback_query(call.id, f"تم حذف الرد التلقائي: {key}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "هذا الرد غير موجود")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("إضافة رد تلقائي ") and is_admin(m.from_user.id))
def add_autoreply(message):
    try:
        _, key, val = message.text.split(" ", 2)
        autoreplies = load_data(FILES["autoreplies"])
        autoreplies[key] = val
        save_data(FILES["autoreplies"], autoreplies)
        bot.reply_to(message, f"✅ تم إضافة الرد التلقائي: {key}")
    except:
        bot.reply_to(message, "❌ الصيغة خاطئة. مثال: إضافة رد تلقائي مرحبا أهلا")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("حذف رد تلقائي ") and is_admin(m.from_user.id))
def del_autoreply(message):
    try:
        key = message.text.split(" ", 2)[2]
        autoreplies = load_data(FILES["autoreplies"])
        if key in autoreplies:
            autoreplies.pop(key)
            save_data(FILES["autoreplies"], autoreplies)
            bot.reply_to(message, f"✅ تم حذف الرد التلقائي: {key}")
        else:
            bot.reply_to(message, "🚫 الرد غير موجود")
    except:
        bot.reply_to(message, "❌ الصيغة خاطئة. مثال: حذف رد تلقائي مرحبا")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("تحذير مستخدم") and m.reply_to_message and is_admin(m.from_user.id))
def warn_user_cmd(message):
    uid = str(message.reply_to_message.from_user.id)
    reason = "تحذير من الأدمن"
    warn_user(uid, message.chat.id, reason)

@bot.message_handler(func=lambda m: m.text=="عرض التحذيرات" and is_admin(m.from_user.id))
def show_warnings(message):
    warnings = load_data(FILES["warnings"])
    if warnings:
        text = "⚠️ تحذيرات المستخدمين:\n"
        for uid,count in warnings.items():
            text += f"- {uid}: {count} تحذيرات\n"
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "🚫 لا يوجد تحذيرات")

@bot.message_handler(func=lambda m: m.text=="عدد المستخدمين" and is_admin(m.from_user.id))
def count_users(message):
    users = load_data(FILES["users"])
    bot.reply_to(message, f"👥 عدد المستخدمين: {len(users)}")

broadcast_states = {}

@bot.message_handler(func=lambda m: m.text=="ارسال جماعي" and is_admin(m.from_user.id))
def start_broadcast(message):
    broadcast_states[message.from_user.id] = True
    bot.reply_to(message, "✉️ ارسل الرسالة التي تريد إرسالها لجميع المستخدمين:")

@bot.message_handler(func=lambda m: broadcast_states.get(m.from_user.id, False))
def do_broadcast(message):
    broadcast_states.pop(message.from_user.id, None)
    users = load_data(FILES["users"])
    count = 0
    for uid in users.keys():
        try:
            bot.send_message(int(uid), message.text)
            count += 1
        except:
            pass
    bot.reply_to(message, f"✅ تم ارسال الرسالة لـ {count} مستخدم.")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    uid = str(message.from_user.id)
    text = message.text or ""

    users = load_data(FILES["users"])
    if uid not in users:
        users[uid] = message.from_user.first_name
        save_data(FILES["users"], users)

    stats = load_data(FILES["stats"])
    stats["messages"] = stats.get("messages",0) + 1
    save_data(FILES["stats"], stats)

    logs = load_data(FILES["logs"])
    logs.setdefault(uid, []).append({"text": text, "time": str(datetime.now())})
    if len(logs[uid]) > 20:
        logs[uid] = logs[uid][-20:]
    save_data(FILES["logs"], logs)

    bans = load_data(FILES["bans"])
    if uid in bans:
        if isinstance(bans[uid], float) and time.time() > bans[uid]:
            bans.pop(uid)
            save_data(FILES["bans"], bans)
        else:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            return

    mutes = load_data(FILES["mutes"])
    if uid in mutes:
        mute_val = mutes[uid]
        if isinstance(mute_val, float):
            if time.time() > mute_val:
                mutes.pop(uid)
                save_data(FILES["mutes"], mutes)
            else:
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                except:
                    pass
                return
        else:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            return

    filters = load_data(FILES["filters"])
    if filters.get("enabled", True):
        badwords = ["غبي", "تافه", "حقير"]
        if any(w in text.lower() for w in badwords):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            warn_user(uid, message.chat.id, "كلمات مسيئة")
            return
        if "http://" in text.lower() or "https://" in text.lower() or "t.me/" in text.lower():
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            warn_user(uid, message.chat.id, "روابط ممنوعة")
            return

    autoreplies = load_data(FILES["autoreplies"])
    for key, val in autoreplies.items():
        if key in text:
            bot.reply_to(message, val)
            break

def warn_user(uid, chat_id, reason):
    warnings = load_data(FILES["warnings"])
    warnings[uid] = warnings.get(uid, 0) + 1
    count = warnings[uid]
    save_data(FILES["warnings"], warnings)
    bot.send_message(chat_id, f"⚠️ تحذير {count}/3 بسبب: {reason}")
    if count >= 3:
        bans = load_data(FILES["bans"])
        if uid not in bans:
            bans[uid] = True
            save_data(FILES["bans"], bans)
            bot.send_message(chat_id, f"🚫 تم حظر المستخدم {uid}")

print("✅ بوت ماريا المطور جاهز للعمل")
bot.infinity_polling()
