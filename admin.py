import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

OWNER_ID = 8011996271
STATE_FILE = "bot_state.json"

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
            content = f.read().strip()
            if not content:
                save_state(default_state)
                return default_state
            return json.loads(content)
    except Exception:
        save_state(default_state)
        return default_state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ هذا الأمر خاص بالمالك فقط.")
        return

    state = load_state()
    bot_status = "✅ مفعل" if state["bot_enabled"] else "❌ معطل"
    welcome_status = "✅ مفعل" if state["welcome_enabled"] else "❌ معطل"
    channels = state.get("subscription_channels", [])
    subs_count = len(channels)

    buttons = [
        [InlineKeyboardButton(f"تفعيل البوت {'✅' if not state['bot_enabled'] else '❌'}", callback_data="bot_toggle")],
        [InlineKeyboardButton(f"تفعيل شعار الدخول {'✅' if not state['welcome_enabled'] else '❌'}", callback_data="welcome_toggle")],
        [InlineKeyboardButton("إضافة قناة للاشتراك", callback_data="add_channel")],
        [InlineKeyboardButton("حذف قناة للاشتراك", callback_data="remove_channel")],
        [InlineKeyboardButton("عرض قنوات الاشتراك", callback_data="show_channels")],
        [InlineKeyboardButton("إرسال إذاعة في الجروبات", callback_data="broadcast_groups")],
        [InlineKeyboardButton("إرسال إذاعة في الخاص", callback_data="broadcast_private")],
        [InlineKeyboardButton("عرض الإحصائيات", callback_data="show_stats")],
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
    channels = state.get("subscription_channels", [])

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
        await query.message.reply_text("اختر القناة التي تريد حذفها:", reply_markup=kb)
        await query.answer()
        return

    if data.startswith("remove_channel_"):
        ch_to_remove = data[len("remove_channel_"):]
        if ch_to_remove in channels:
            channels.remove(ch_to_remove)
            state["subscription_channels"] = channels
            save_state(state)
            await query.answer(f"تم حذف القناة {ch_to_remove}.")
            await show_admin_panel(update, context)
        else:
            await query.answer("القناة غير موجودة.", show_alert=True)
        return

    if data == "show_channels":
        if not channels:
            await query.answer("لا توجد قنوات للاشتراك.", show_alert=True)
            return
        text = "📢 قنوات الاشتراك الإجباري:\n" + "\n".join(channels)
        await query.answer()
        await query.message.reply_text(text)
        return

    # أزرار أخرى مثل الإذاعة والإحصائيات ممكن تضيفها هنا بنفس الطريقة

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return

    text = update.message.text.strip()
    state = load_state()
    channels = state.get("subscription_channels", [])

    if context.user_data.get("waiting_for_channel_add"):
        if not text.startswith("@"):
            await update.message.reply_text("❌ الرجاء إرسال معرف القناة بشكل صحيح (ابدأ بـ @).")
            return
        if text in channels:
            await update.message.reply_text("❌ القناة موجودة مسبقًا.")
        else:
            channels.append(text)
            state["subscription_channels"] = channels
            save_state(state)
            await update.message.reply_text(f"✅ تم إضافة القناة {text}.")
        context.user_data["waiting_for_channel_add"] = False
        return
