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

def load_channels():
    default_channels = []
    if not os.path.exists(CHANNELS_FILE):
        save_channels(default_channels)
        return default_channels
    try:
        with open(CHANNELS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                save_channels(default_channels)
                return default_channels
            return json.loads(content)
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
        [InlineKeyboardButton("عرض الإحصائيات", callback_data="show_stats")],
        [InlineKeyboardButton("رفع مشرف", callback_data="promote_admin")],
        [InlineKeyboardButton("تنزيل مشرف", callback_data="demote_admin")],
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
        await query.message.reply_text("اختر القناة التي تريد حذفها:", reply_markup=kb)
        await query.answer()
        return

    if data.startswith("remove_channel_"):
        ch_to_remove = data[len("remove_channel_"):]
        if ch_to_remove in channels:
            channels.remove(ch_to_remove)
            save_channels(channels)
            await query.answer(f"تم حذف القناة {ch_to_remove}.")
            await show_admin_panel(update, context)
        else:
            await query.answer("القناة غير موجودة.", show_alert=True)
        return

    if data == "broadcast_groups":
        await query.message.reply_text("أرسل الرسالة التي تريد إذاعتها في جميع المجموعات:")
        context.user_data["waiting_broadcast_groups"] = True
        await query.answer()
        return

    if data == "broadcast_private":
        await query.message.reply_text("أرسل الرسالة التي تريد إذاعتها في الخاص:")
        context.user_data["waiting_broadcast_private"] = True
        await query.answer()
        return

    if data == "show_stats":
        users_count = 0
        groups_count = 0
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                users_count = len(f.read().splitlines())
        if os.path.exists("groups.txt"):
            with open("groups.txt", "r") as f:
                groups_count = len(f.read().splitlines())
        await query.answer()
        await query.edit_message_text(f"📊 إحصائيات البوت:\nعدد المستخدمين: {users_count}\nعدد المجموعات: {groups_count}")
        return

    if data == "promote_admin":
        await query.message.reply_text("أرسل معرف المستخدم الذي تريد رفعه مشرف:")
        context.user_data["waiting_promote"] = True
        await query.answer()
        return

    if data == "demote_admin":
        await query.message.reply_text("أرسل معرف المستخدم الذي تريد تنزيله من المشرفين:")
        context.user_data["waiting_demote"] = True
        await query.answer()
        return

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return

    text = update.message.text.strip()
    channels = load_channels()

    if context.user_data.get("waiting_for_channel_add"):
        if not text.startswith("@"):
            await update.message.reply_text("❌ الرجاء إرسال معرف القناة بشكل صحيح (ابدأ بـ @).")
            return
        if text in channels:
            await update.message.reply_text("❌ القناة موجودة مسبقًا.")
        else:
            channels.append(text)
            save_channels(channels)
            await update.message.reply_text(f"✅ تم إضافة القناة {text}.")
        context.user_data["waiting_for_channel_add"] = False
        return

    if context.user_data.get("waiting_broadcast_groups"):
        sent, failed = 0, 0
        if os.path.exists("groups.txt"):
            with open("groups.txt", "r") as f:
                groups = f.read().splitlines()
            for gid in groups:
                try:
                    await context.bot.send_message(int(gid), text=text)
                    sent += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    failed += 1
        await update.message.reply_text(f"✅ تم الإرسال إلى {sent} مجموعة.\n❌ فشل الإرسال في {failed} مجموعة.")
        context.user_data["waiting_broadcast_groups"] = False
        return

    if context.user_data.get("waiting_broadcast_private"):
        sent, failed = 0, 0
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                users = f.read().splitlines()
            for uid in users:
                try:
                    await context.bot.send_message(int(uid), text=text)
                    sent += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    failed += 1
        await update.message.reply_text(f"✅ تم الإرسال في الخاص إلى {sent} مستخدم.\n❌ فشل الإرسال لـ {failed} مستخدم.")
        context.user_data["waiting_broadcast_private"] = False
        return

    if context.user_data.get("waiting_promote"):
        try:
            user_to_promote = int(text)
            await context.bot.promote_chat_member(
                update.effective_chat.id,
                user_to_promote,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True
            )
            await update.message.reply_text(f"✅ تم رفع المستخدم {user_to_promote} مشرف.")
        except Exception as e:
            await update.message.reply_text(f"❌ فشل رفع المشرف: {e}")
        context.user_data["waiting_promote"] = False
        return

    if context.user_data.get("waiting_demote"):
        try:
            user_to_demote = int(text)
            await context.bot.promote_chat_member(
                update.effective_chat.id,
                user_to_demote,
                can_change_info=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False
            )
            await update.message.reply_text(f"✅ تم تنزيل المستخدم {user_to_demote} من المشرفين.")
        except Exception as e:
            await update.message.reply_text(f"❌ فشل تنزيل المشرف: {e}")
        context.user_data["waiting_demote"] = False
        return
