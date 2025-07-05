from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import random

async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🎲 حجر نرد", callback_data="game_dice")],
        [InlineKeyboardButton("🎯 هدف عشوائي", callback_data="game_dart")],
        [InlineKeyboardButton("⚽ كرة القدم", callback_data="game_ball")],
        [InlineKeyboardButton("🏀 كرة السلة", callback_data="game_basket")],
        [InlineKeyboardButton("🎰 سلوت", callback_data="game_slot")],
        [InlineKeyboardButton("❓ احزر الرقم", callback_data="game_guess")],
        [InlineKeyboardButton("🧠 سؤال عشوائي", callback_data="game_question")],
        [InlineKeyboardButton("🎮 تحدي سرعة", callback_data="game_fast")],
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🎮 اختر لعبة من القائمة:", reply_markup=keyboard)

async def handle_game_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user.first_name

    if data == "game_dice":
        await query.message.reply_dice("🎲")

    elif data == "game_dart":
        await query.message.reply_dice("🎯")

    elif data == "game_ball":
        await query.message.reply_dice("⚽")

    elif data == "game_basket":
        await query.message.reply_dice("🏀")

    elif data == "game_slot":
        await query.message.reply_dice("🎰")

    elif data == "game_guess":
        number = random.randint(1, 5)
        await query.message.reply_text(f"🤔 حاول تخمين رقم من 1 إلى 5...\n🔢 الرقم هو: {number}")

    elif data == "game_question":
        questions = [
            "❓ كم عدد قارات العالم؟",
            "❓ من هو مخترع المصباح الكهربائي؟",
            "❓ كم عدد أضلاع المثلث؟",
            "❓ ما عاصمة اليابان؟",
        ]
        q = random.choice(questions)
        await query.message.reply_text(f"{user}🧠: {q}")

    elif data == "game_fast":
        await query.message.reply_text(f"⚡ {user}، أول من يكتب كلمة (برق) يفوز!")