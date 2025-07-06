from telegram import Update
from telegram.ext import ContextTypes
import random

active_guess = {}
active_fast = {}
ttt_games = {}

# ===== لعبة خمن الرقم =====
async def start_guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_guess:
        await update.message.reply_text("🎯 لعبة خمن شغالة بالفعل. حاول تخمين الرقم!")
        return
    number = random.randint(1, 20)
    active_guess[chat_id] = number
    await update.message.reply_text("🎯 بدأت لعبة خمن الرقم! اختر رقم بين 1 و 20")

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in active_guess:
        return
    try:
        guess = int(update.message.text.strip())
    except ValueError:
        return
    correct = active_guess[chat_id]
    if guess == correct:
        await update.message.reply_text(f"🎉 مبروك! الرقم الصحيح هو {correct}.")
        del active_guess[chat_id]
    elif guess < correct:
        await update.message.reply_text("🔼 أكبر")
    else:
        await update.message.reply_text("🔽 أصغر")

# ===== لعبة الأسرع كتابة =====
fast_words = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
    "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚",
    "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🥸",
    "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️",
    "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡",
    "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓",
    "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄",
    "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵",
    "🤐", "🥴", "🤢", "🤮", "🤧", "😷"
]

async def start_fast_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_fast:
        await update.message.reply_text("⚡ لعبة الأسرع شغالة! اكتب الإيموجي بسرعة!")
        return
    word = random.choice(fast_words)
    active_fast[chat_id] = word
    await update.message.reply_text(f"📝 أرسل الإيموجي التالي بسرعة: {word}")

async def handle_fast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in active_fast:
        return
    if update.message.text.strip() == active_fast[chat_id]:
        await update.message.reply_text("🎉 أحسنت، أنت الأسرع!")
        del active_fast[chat_id]

# ===== لعبة اكس او =====
TTT_SYMBOLS = ['❌', '⭕']

async def start_ttt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in ttt_games:
        await update.message.reply_text("❌ لعبة اكس او شغالة حالياً")
        return
    ttt_games[chat_id] = {
        "board": [' '] * 9,
        "turn": 0
    }
    await update.message.reply_text("🎮 بدأت لعبة اكس او! اكتب رقم بين 1-9 لوضع الرمز.")
    await display_board(update, context)

async def handle_ttt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in ttt_games:
        return
    try:
        pos = int(update.message.text.strip()) - 1
        if not (0 <= pos <= 8):
            return
    except ValueError:
        return
    game = ttt_games[chat_id]
    if game["board"][pos] != ' ':
        await update.message.reply_text("❗ هذا المكان مأخوذ")
        return
    symbol = TTT_SYMBOLS[game["turn"] % 2]
    game["board"][pos] = symbol
    game["turn"] += 1
    await display_board(update, context)
    winner = check_winner(game["board"])
    if winner:
        await update.message.reply_text(f"🏆 الفائز: {winner}!")
        del ttt_games[chat_id]
    elif ' ' not in game["board"]:
        await update.message.reply_text("🤝 تعادل!")
        del ttt_games[chat_id]

async def display_board(update, context):
    chat_id = update.effective_chat.id
    board = ttt_games[chat_id]["board"]
    board_str = ""
    for i in range(0, 9, 3):
        row = [cell if cell != ' ' else str(i + j + 1) for j, cell in enumerate(board[i:i+3])]
        board_str += ' | '.join(row) + "\\n"
    await context.bot.send_message(chat_id=chat_id, text=board_str)

def check_winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for i,j,k in wins:
        if board[i] == board[j] == board[k] != ' ':
            return board[i]
    return None

# ===== قائمة الألعاب =====
async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 الألعاب المتوفرة:\\n"
        "- اكس او\\n"
        "- خمن\\n"
        "- الاسرع\\n\\n"
        "✏️ أرسل *اسم اللعبة* لبدء اللعب!"
)
