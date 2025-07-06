import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

OWNER_ID = 8011996271
STATE_FILE = "bot_state.json"
CHANNELS_FILE = "channels.json"

def load_state():
    default_state = {
        "bot_enabled": True,
        "welcome_enabled": True,
        "subscription_channels": []
    }
    if not os.path.exists(STATE_FILE):
        save_state(default_state)
        return default_state
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        save_state(default_state)
        return default_state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_channels():
    default_channels = []
    if not os.path.exists(CHANNELS_FILE):
        save_channels(default_channels)
        return default_channels
    try:
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        save_channels(default_channels)
        return default_channels

def save_channels(channels):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(channels, f)

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ هذا الأمر خاص بالمالك فقط.")
        return
    state = load_state()
    bot_status = "✅ مفعل" if state["bot_enabled"] else "❌ معطل"
    welcome_status = "✅ مفعل" if state["welcome_enabled"] else "❌ معطل"
    subs_count = len(state["subscription_channels"])
    buttons = [
        [InlineKeyboardButton(f"تفعيل البوت {'✅' if not state['bot_enabled'] else '❌'}", callback_data="bot_toggle")],
        [InlineKeyboardButton(f"تفعيل شعار الدخول {'✅' if not state['welcome_enabled'] else '❌'}", callback_data="welcome_toggle")],
        [InlineKeyboardButton("إضافة قناة للاشتراك", callback_data="add_channel")],
        [InlineKeyboardButton("حذف قناة للاشتراك", callback_data="remove_channel")],
        [InlineKeyboardButton("إرسال إذاعة في الجروبات", callback_data="broadcast_groups")],
        [InlineKeyboardButton("إرسال إذاعة في الخاص", callback_data="broadcast_private")],
    ]
    kb = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        f"لوحة تحكم المالك:\n\n"
        f"حالة البوت: {bot_status}\n"
        f"حالة شعار الدخول: {welcome_status}\n"
        f"عدد قنوات الاشتراك: {subs_count}",
        reply_markup=kb
    )

async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id != OWNER_ID:
        await query.answer("❌ فقط المالك يمكنه استخدام هذه الأزرار.", show_alert=True)
        return
    data = query.data
    state = load_state()
    channels = load_channels()
    if data == "bot_toggle":
        state["bot_enabled"] = not state["bot_enabled"]
        save_state(state)
        await query.answer(f"تم {'تفعيل' if state['bot_enabled'] else 'تعطيل'} البوت.")
        await show_admin_panel(update, context)
        return
    if data == "welcome_toggle":
        state["welcome_enabled"] = not state["welcome_enabled"]
        save_state(state)
        await query.answer(f"تم {'تفعيل' if state['welcome_enabled'] else 'تعطيل'} شعار الدخول.")
        await show_admin_panel(update, context)
        return
    if data == "add_channel":
        await query.message.reply_text("أرسل معرف القناة الآن (مثال: @channelusername):")
        context.user_data["waiting_for_channel_add"] = True
        await query.answer()
        return
    if data == "remove_channel":
        if not channels:
            await query.answer("لا توجد قنوات للاشتراك.", show_alert=True)
            return
        buttons = [[InlineKeyboardButton(ch, callback_data=f"remove_channel_{ch}")] for ch in channels]
        kb = InlineKeyboardMarkup(buttons)
        await query.message.reply_text("اختر القناة التي تريد حذفها:", reply_markup=kb
