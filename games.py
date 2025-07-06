from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import random

# ذاكرة مؤقتة لتخزين حالات المستخدم
user_game_state = {}

# عرض قائمة الألعاب
async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🎲 حجر ورقة مقص", callback_data="game_rps")],
        [InlineKeyboardButton("🎯 تخمين رقم", callback_data="game_guess")],
        [InlineKeyboardButton("🧠 سؤال عام", callback_data="game_quiz")],
        [InlineKeyboardButton("⌨️ سرعة الكتابة", callback_data="game_typing")],
        [InlineKeyboardButton("🔢 رياضيات", callback_data="game_math")],
        [InlineKeyboardButton("😹 نكتة", callback_data="game_joke")],
        [InlineKeyboardButton("🎵 كلمات أغاني", callback_data="game_lyrics")],
        [InlineKeyboardButton("😼 لعبة كت", callback_data="game_cat")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🎮 اختر لعبة:", reply_markup=keyboard)

# التعامل مع الضغط على الأزرار
async def handle_game_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    game = query.data

    # حجر ورقة مقص
    if game == "game_rps":
        choices = ["حجر", "ورقة", "مقص"]
        bot_choice = random.choice(choices)
        user_game_state[user_id] = {"game": "rps", "bot_choice": bot_choice}
        await query.message.reply_text("✊✋✌️ اكتب: حجر أو ورقة أو مقص")

    # تخمين رقم
    elif game == "game_guess":
        number = random.randint(1, 5)
        user_game_state[user_id] = {"game": "guess", "number": number}
        await query.message.reply_text("🎯 خمن رقم من 1 إلى 5!")

    # سؤال عام
    elif game == "game_quiz":
        user_game_state[user_id] = {"game": "quiz", "answer": "طوكيو"}
        await query.message.reply_text("🧠 ما هي عاصمة اليابان؟")

    # سرعة الكتابة
    elif game == "game_typing":
        word = random.choice(["تفاحة", "قطار", "مدرسة", "برمجة"])
        user_game_state[user_id] = {"game": "typing", "word": word}
        await query.message.reply_text(f"⌨️ اكتب الكلمة التالية بأسرع وقت: {word}")

    # رياضيات
    elif game == "game_math":
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        user_game_state[user_id] = {"game": "math", "answer": str(a + b)}
        await query.message.reply_text(f"🔢 ما ناتج: {a} + {b} ؟")

    # نكتة
    elif game == "game_joke":
        jokes = [
            "😂 واحد راح للدكتور قاله عيني بتدمع، قله غني لها.",
            "🤣 واحد راح المدرسة متأخر، قاله المدير: ليش؟ قاله: الطريق طويل!",
            "😹 مرة واحد نام بكير... صحى بدري، لقى الدنيا ليل!"
        ]
        await query.message.reply_text(random.choice(jokes))

    # كلمات أغاني
    elif game == "game_lyrics":
        await query.message.reply_text("🎶 أكمل: يا طيبة... يا طيبة... 💙")

    # لعبة كت
    elif game == "game_cat":
        await query.message.reply_text(
            "😼 بوت كت:\n- أنت: مرحبًا\n- البوت: أهلًا بالحلو! وينك؟\n- أنت: مشغول\n- البوت: مشغول عني؟ 😾"
        )

# التحقق من رد المستخدم بعد اللعبة
async def handle_text_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in user_game_state:
        state = user_game_state[user_id]
        game = state["game"]

        if game == "rps":
            user = text
            bot = state["bot_choice"]
            if user not in ["حجر", "ورقة", "مقص"]:
                await update.message.reply_text("❗ اختر: حجر، ورقة، أو مقص.")
                return
            if user == bot:
                result = "🤝 تعادل!"
            elif (user == "حجر" and bot == "مقص") or (user == "ورقة" and bot == "حجر") or (user == "مقص" and bot == "ورقة"):
                result = f"✅ فزت! (البوت اختار {bot})"
            else:
                result = f"❌ خسرت! (البوت اختار {bot})"
            await update.message.reply_text(result)

        elif game == "guess":
            if text.isdigit() and int(text) == state["number"]:
                await update.message.reply_text("🎯 صحيح! خمنت الرقم!")
            else:
                await update.message.reply_text(f"❌ خطأ! الرقم كان {state['number']}")

        elif game == "quiz":
            if "طوكيو" in text:
                await update.message.reply_text("✅ إجابة صحيحة!")
            else:
                await update.message.reply_text("❌ خطأ! الإجابة: طوكيو")

        elif game == "typing":
            if text == state["word"]:
                await update.message.reply_text("✅ ممتاز! كتبتها صح")
            else:
                await update.message.reply_text(f"❌ خطأ! الكلمة كانت: {state['word']}")

        elif game == "math":
            if text == state["answer"]:
                await update.message.reply_text("✅ صحيح!")
            else:
                await update.message.reply_text(f"❌ خطأ! الجواب هو: {state['answer']}")

        # احذف الحالة بعد الانتهاء
        del user_game_state[user_id]
