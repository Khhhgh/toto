from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def make_keyboard(buttons):
    keyboard_buttons = []
    for row in buttons:
        keyboard_buttons.append([InlineKeyboardButton(text=btn['text'], url=btn.get('url', None)) for btn in row])
    return InlineKeyboardMarkup(keyboard_buttons)
