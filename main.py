import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

DEVELOPER_ID = 8011996271  # << ضع معرفك هنا
CHANNEL_FILE = "channel.json"

def save_channel(username):
    with open(CHANNEL_FILE, "w") as f:
        json.dump({"channel": username}, f)

def load_channel():
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, "r") as f:
            return json.load(f).get("channel")
    return None

async def check_subscription(user_id, context):
    channel = load_channel()
    if not channel:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first = update.effective_user.first_name
    text = f"👋 أهلاً بك {first} في البوت الخدمي 🎉\nاختر من الأزرار بالأسفل:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 حسابي", callback_data="account")],
        [InlineKeyboardButton("🎮 الألعاب", callback_data="games")],
        [InlineKeyboardButton("🛠 الأدوات", callback_data="tools")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)
    return

    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        channel = load_channel()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 اشترك بالقناة", url=f"https://t.me/{channel.strip('@')}")],
            [InlineKeyboardButton("✅ تحققت", callback_data="check_sub")]
        ])
        await update.message.reply_text("📌 اشترك في القناة للاستمرار:", reply_markup=keyboard)
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ تعيين قناة الاشتراك", callback_data="set_channel")]
    ])
    await update.message.reply_text("👋 أهلاً بك في بوت الإدارة.", reply_markup=keyboard)

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if await check_subscription(user_id, context):
        await query.edit_message_text("✅ تم التحقق من الاشتراك.")
    else:
        await query.edit_message_text("❌ لم يتم الاشتراك بعد.")

async def set_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != DEVELOPER_ID:
        await query.answer("❌ غير مصرح لك.", show_alert=True)
        return
    await query.edit_message_text("📥 أرسل الآن معرف القناة بصيغة: @channel")
    context.user_data["set_channel"] = True

async def handle_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("set_channel") and update.effective_user.id == DEVELOPER_ID:
        text = update.message.text.strip()
        if text.startswith("@"):
            save_channel(text)
            await update.message.reply_text(f"✅ تم حفظ القناة: {text}")
            context.user_data["set_channel"] = False
        else:
            await update.message.reply_text("⚠️ يجب أن يبدأ المعرف بـ @")

if __name__ == "__main__":
    TOKEN = "7547739104:AAHkVp4JZ6Sr3PMEPWvfY-XrJ7-mtEFLEUw"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="check_sub"))
    app.add_handler(CallbackQueryHandler(set_channel_callback, pattern="set_channel"))
    app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_channel_input))

    app.run_polling()

from telegram import ChatPermissions

async def is_admin(update, context):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)
    return member.status in ["administrator", "creator"]

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("🚫 فقط المشرفين يمكنهم استخدام هذا الأمر.")
    if update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=update.message.reply_to_message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text("🔇 تم كتم العضو.")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("🚫 فقط المشرفين يمكنهم استخدام هذا الأمر.")
    if update.message.reply_to_message:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=update.message.reply_to_message.from_user.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        await update.message.reply_text("🔊 تم فك الكتم.")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("🚫 فقط المشرفين يمكنهم استخدام هذا الأمر.")
    if update.message.reply_to_message:
        await context.bot.ban_chat_member(chat_id=update.effective_chat.id,
                                          user_id=update.message.reply_to_message.from_user.id)
        await context.bot.unban_chat_member(chat_id=update.effective_chat.id,
                                            user_id=update.message.reply_to_message.from_user.id)
        await update.message.reply_text("👢 تم طرد العضو.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("🚫 فقط المشرفين يمكنهم استخدام هذا الأمر.")
    if update.message.reply_to_message:
        await context.bot.ban_chat_member(chat_id=update.effective_chat.id,
                                          user_id=update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🚫 تم حظر العضو.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("🚫 فقط المشرفين يمكنهم استخدام هذا الأمر.")
    if update.message.reply_to_message:
        await context.bot.unban_chat_member(chat_id=update.effective_chat.id,
                                            user_id=update.message.reply_to_message.from_user.id)
        await update.message.reply_text("✅ تم فك الحظر.")

async def restrict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("🚫 فقط المشرفين يمكنهم استخدام هذا الأمر.")
    if update.message.reply_to_message:
        perms = ChatPermissions(can_send_messages=False, can_send_media_messages=False)
        await context.bot.restrict_chat_member(update.effective_chat.id,
                                               update.message.reply_to_message.from_user.id,
                                               permissions=perms)
        await update.message.reply_text("⛔️ تم تقييد العضو.")

async def unrestrict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("🚫 فقط المشرفين يمكنهم استخدام هذا الأمر.")
    if update.message.reply_to_message:
        perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                can_send_other_messages=True, can_add_web_page_previews=True)
        await context.bot.restrict_chat_member(update.effective_chat.id,
                                               update.message.reply_to_message.from_user.id,
                                               permissions=perms)
        await update.message.reply_text("✅ تم فك التقييد.")

app.add_handler(CommandHandler("كتم", mute))
app.add_handler(CommandHandler("فك_الكتم", unmute))
app.add_handler(CommandHandler("طرد", kick))
app.add_handler(CommandHandler("حظر", ban))
app.add_handler(CommandHandler("فك_الحظر", unban))
app.add_handler(CommandHandler("تقييد", restrict))
app.add_handler(CommandHandler("فك_التقييد", unrestrict))


import random
import asyncio

questions = [
    ("ما عاصمة العراق؟", ["بغداد", "دمشق", "عمان"], "بغداد"),
    ("كم عدد الكواكب؟", ["8", "9", "7"], "8"),
    ("أين يقع برج إيفل؟", ["باريس", "روما", "لندن"], "باريس"),
    ("ما لون السماء؟", ["أزرق", "أخضر", "أحمر"], "أزرق"),
]

true_false = [
    ("الشمس أقرب إلى الأرض من القمر", False),
    ("العراق بلد عربي", True),
    ("الإنترنت اخترع قبل التلفاز", False),
]

words_to_unscramble = ["مدرسة", "كمبيوتر", "برمجة", "سيارة", "شباك"]

async def roll_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_dice(chat_id=update.effective_chat.id)

async def rock_paper_scissors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choices = ["🪨 حجر", "📄 ورقة", "✂️ مقص"]
    choice = random.choice(choices)
    await update.message.reply_text(f"🤖 اختار: {choice}")

async def guess_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 5)
    context.user_data["guess_number"] = number
    await update.message.reply_text("🎯 خمن رقماً من 1 إلى 5")

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "guess_number" in context.user_data:
        try:
            guess = int(update.message.text.strip())
            if guess == context.user_data["guess_number"]:
                await update.message.reply_text("🎉 صحيح!")
            else:
                await update.message.reply_text(f"❌ خطأ، الرقم هو {context.user_data['guess_number']}")
            del context.user_data["guess_number"]
        except:
            pass

async def speed_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاوب خلال 10 ثواني: كم 5 + 7 ؟")
    context.user_data["speed_answer"] = True
    await asyncio.sleep(10)
    if context.user_data.get("speed_answer"):
        await update.message.reply_text("⏱ انتهى الوقت!")
        del context.user_data["speed_answer"]

async def handle_speed_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("speed_answer"):
        if update.message.text.strip() == "12":
            await update.message.reply_text("✅ إجابة صحيحة وسريعة!")
        else:
            await update.message.reply_text("❌ إجابة خاطئة.")
        del context.user_data["speed_answer"]

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, options, answer = random.choice(questions)
    "msg = f"❓ {q}
"
    for opt in options:
        msg += f"- {opt}
"
    context.user_data["quiz_answer"] = answer
    await update.message.reply_text(msg.strip())

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "quiz_answer" in context.user_data:
        if update.message.text.strip() == context.user_data["quiz_answer"]:
            await update.message.reply_text("🎉 إجابة صحيحة!")
        else:
            await update.message.reply_text(f"❌ خطأ! الجواب الصحيح: {context.user_data['quiz_answer']}")
        del context.user_data["quiz_answer"]

async def random_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emojis = ["😂", "🔥", "❤️", "👍", "🎉", "💯", "🌟", "🚀"]
    await update.message.reply_text(random.choice(emojis))

async def scramble_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(words_to_unscramble)
    scrambled = ''.join(random.sample(word, len(word)))
    context.user_data["scramble_word"] = word
    await update.message.reply_text(f"🔤 رتب هذه الكلمة: {scrambled}")

async def handle_scramble_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "scramble_word" in context.user_data:
        if update.message.text.strip() == context.user_data["scramble_word"]:
            await update.message.reply_text("✅ صحيح!")
        else:
            await update.message.reply_text(f"❌ خطأ! الكلمة هي: {context.user_data['scramble_word']}")
        del context.user_data["scramble_word"]

async def true_or_false(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, a = random.choice(true_false)
    context.user_data["true_false"] = a
    await update.message.reply_text(f"❓ صح أم خطأ: {q}")

async def handle_true_false(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "true_false" in context.user_data:
        ans = update.message.text.strip().lower()
        correct = context.user_data["true_false"]
        if (ans == "صح" and correct) or (ans == "خطأ" and not correct):
            await update.message.reply_text("✅ إجابة صحيحة!")
        else:
            await update.message.reply_text("❌ إجابة خاطئة.")
        del context.user_data["true_false"]

app.add_handler(CommandHandler("نرد", roll_dice))
app.add_handler(CommandHandler("حجر_ورقة_مقص", rock_paper_scissors))
app.add_handler(CommandHandler("خمن", guess_number))
app.add_handler(CommandHandler("سرعة", speed_question))
app.add_handler(CommandHandler("سؤال", ask_question))
app.add_handler(CommandHandler("ايموجي", random_emoji))
app.add_handler(CommandHandler("رتب", scramble_word))
app.add_handler(CommandHandler("صح_خطأ", true_or_false))

app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_guess))
app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_speed_answer))
app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_quiz_answer))
app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_scramble_answer))
app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_true_false))


import time

BANK_FILE = "bank.json"

def load_bank():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, "r") as f:
            return json.load(f)
    return {}

def save_bank(data):
    with open(BANK_FILE, "w") as f:
        json.dump(data, f)

def get_user_data(user_id):
    bank = load_bank()
    if str(user_id) not in bank:
        bank[str(user_id)] = {"balance": 0, "last_salary": 0}
        save_bank(bank)
    return bank[str(user_id)]

def update_user_data(user_id, data):
    bank = load_bank()
    bank[str(user_id)] = data
    save_bank(bank)

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id)
    await update.message.reply_text(f"💰 رصيدك: {data['balance']} دينار")

async def get_salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id)
    now = time.time()
    if now - data['last_salary'] >= 86400:  # كل 24 ساعة
        data['balance'] += 100
        data['last_salary'] = now
        update_user_data(user.id, data)
        await update.message.reply_text("✅ تم صرف الراتب اليومي: 100 دينار")
    else:
        remain = int(86400 - (now - data['last_salary']))
        hours = remain // 3600
        minutes = (remain % 3600) // 60
        await update.message.reply_text(f"⌛ يمكنك أخذ الراتب بعد {hours} ساعة و{minutes} دقيقة")

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2 or not context.args[1].isdigit():
        return await update.message.reply_text("⚠️ الصيغة: /تحويل @user 100")
    target_username = context.args[0].lstrip('@')
    amount = int(context.args[1])
    sender = update.effective_user
    if amount <= 0:
        return await update.message.reply_text("⚠️ المبلغ غير صحيح.")

    members = await context.bot.get_chat_administrators(update.effective_chat.id)
    users = [m.user for m in members]
    receiver_id = None
    for user in users:
        if user.username and user.username.lower() == target_username.lower():
            receiver_id = user.id
            break
    if not receiver_id:
        return await update.message.reply_text("❌ لم يتم العثور على المستخدم.")

    sender_data = get_user_data(sender.id)
    if sender_data["balance"] < amount:
        return await update.message.reply_text("❌ لا تملك رصيد كافٍ.")

    receiver_data = get_user_data(receiver_id)
    sender_data["balance"] -= amount
    receiver_data["balance"] += amount

    update_user_data(sender.id, sender_data)
    update_user_data(receiver_id, receiver_data)

    await update.message.reply_text(f"✅ تم تحويل {amount} دينار إلى @{target_username}")

async def steal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ استخدم الأمر بالرد على رسالة الشخص المستهدف.")
    thief = update.effective_user
    target = update.message.reply_to_message.from_user
    if thief.id == target.id:
        return await update.message.reply_text("❌ لا يمكنك سرقة نفسك!")

    thief_data = get_user_data(thief.id)
    target_data = get_user_data(target.id)
    if target_data["balance"] < 10:
        return await update.message.reply_text("❌ لا يوجد ما يُسرق من هذا الشخص.")

    success = random.choice([True, False])
    amount = random.randint(10, min(50, target_data["balance"]))
    if success:
        thief_data["balance"] += amount
        target_data["balance"] -= amount
        update_user_data(thief.id, thief_data)
        update_user_data(target.id, target_data)
        await update.message.reply_text(f"💸 نجحت في سرقة {amount} دينار من {target.first_name}!")
    else:
        penalty = min(20, thief_data["balance"])
        thief_data["balance"] -= penalty
        update_user_data(thief.id, thief_data)
        await update.message.reply_text(f"🚨 فشلت في السرقة! تم خصم {penalty} دينار منك كعقوبة.")

app.add_handler(CommandHandler("رصيدي", show_balance))
app.add_handler(CommandHandler("راتب", get_salary))
app.add_handler(CommandHandler("تحويل", transfer))
app.add_handler(CommandHandler("سرقة", steal))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "account":
        await show_balance(update, context)
    elif query.data == "games":
        await query.edit_message_text("🎮 استخدم الأوامر:
/نرد - /خمن - /سؤال - /ايموجي - /رتب ...")
    elif query.data == "tools":
        await query.edit_message_text("🛠 أدوات الإدارة:
/كتم - /طرد - /تقييد - /حظر ...")

app.add_handler(CallbackQueryHandler(button_handler, pattern="^(account|games|tools)$"))
