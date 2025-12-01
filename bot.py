# RoseUserBot v3.1 — Railway Ready
# Owner VC control + Safe VC failure (no recording forward)
# Commands:
#   Basic: .start .help .ping .rules
#   Admin: .setrules .kick .ban .unban .mute .unmute
#   Owner: .vcjoin .play .vcleave .spam .unschedule .checkadmin

import asyncio
import time
import logging
import os
from datetime import datetime, timedelta

from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest, EditBannedRequest
from telethon.tl.types import (
    ChatBannedRights,
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
)

# ---------------- CONFIG ----------------
# बेहतर तरीका: Railway में env vars सेट कर देना
API_ID = int(os.getenv("API_ID", "32581893"))
API_HASH = os.getenv("API_HASH", "86d15530bb76890fbed3453d820e94f5")
SESSION_NAME = "RoseUserBot"   # इसी नाम से session file बनेगी

logging.basicConfig(level=logging.WARNING)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Try VC lib
USE_PYTGCALLS = False
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types.input_stream import AudioPiped
    USE_PYTGCALLS = True
except Exception:
    USE_PYTGCALLS = False

pytgcalls = None

# In-memory stores
OWNER_VC_TARGET = {}   # {owner_id: {"chat_id": int}}
SCHEDULES = {}         # {chat_id: asyncio.Task}
GROUP_RULES = {}       # {chat_id: "rules text"}

MIN_INTERVAL = 0.1
MAX_INTERVAL = 600.0
MAX_COUNT = 10000

# ---------------- ROLE HELPERS ----------------
async def is_owner(user_id: int) -> bool:
    me = await client.get_me()
    return user_id == me.id

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        participant = await client(GetParticipantRequest(chat_id, user_id))
        p = participant.participant
        if isinstance(p, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return True
    except Exception:
        pass

    try:
        perms = await client.get_permissions(chat_id, user_id)
        return perms.is_admin or perms.is_creator
    except Exception:
        me = await client.get_me()
        return user_id == me.id

async def get_user_from_event(event, arg=None):
    """Reply या @username से user निकालो."""
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.sender:
            return reply.sender_id, reply.sender.first_name
        return None, None
    if arg:
        try:
            user = await client.get_entity(arg)
            name = getattr(user, "first_name", None) or getattr(user, "username", arg)
            return user.id, name
        except Exception:
            return None, None
    return None, None

# ---------------- BASIC COMMANDS ----------------
@client.on(events.NewMessage(pattern=r'^\.start$', outgoing=True, incoming=True))
async def start_cmd(event):
    me = await client.get_me()
    uname = f"@{me.username}" if me.username else me.first_name
    await event.reply(
        f"🌹 **RoseUserBot v3.1 Active**\n"
        f"👑 Owner: {uname}\n"
        f"ℹ️ Example: `.help` to see all commands."
    )

@client.on(events.NewMessage(pattern=r'^\.help$', outgoing=True, incoming=True))
async def help_cmd(event):
    text = (
        "🌹 **RoseUserBot Commands (Railway Build)**\n\n"
        "🧭 **Basic**\n"
        "• `.start` — Bot info\n"
        "  Example: `.start`\n"
        "• `.help` — This help\n"
        "  Example: `.help`\n"
        "• `.ping` — Ping test\n"
        "  Example: `.ping`\n"
        "• `.rules` — Show group rules\n"
        "  Example: `.rules`\n\n"
        "🛡️ **Admin**\n"
        "• `.setrules <text>` — Set rules\n"
        "  Example: `.setrules Be respectful to everyone.`\n"
        "• `.kick` (reply/@user) — Kick user\n"
        "  Example: Reply to user → `.kick`\n"
        "• `.ban @user` — Ban user\n"
        "  Example: `.ban @spamuser`\n"
        "• `.unban @user` — Unban user\n"
        "  Example: `.unban @spamuser`\n"
        "• `.mute @user 1h` — Mute for time\n"
        "  Example: `.mute @user 30m`\n"
        "• `.unmute @user` — Unmute\n"
        "  Example: `.unmute @user`\n\n"
        "👑 **Owner Only**\n"
        "• `.vcjoin <chat_id>` — Set VC target group/channel\n"
        "  Example: `.vcjoin -1001234567890`\n"
        "• `.play` — Reply to voice/audio, play in VC\n"
        "  Example: Reply to voice → `.play`\n"
        "• `.vcleave` — Leave VC + clear target\n"
        "  Example: `.vcleave`\n"
        "• `.spam <interval> <count> <msg>` — Spam message\n"
        "  Example: `.spam 2 10 Hello!`\n"
        "• `.unschedule` — Stop running spam in this chat\n"
        "  Example: `.unschedule`\n"
        "• `.checkadmin` — Check if you are admin in this chat\n"
        "  Example: `.checkadmin`\n\n"
        "⚠️ VC Note:\n"
        "- Needs `py-tgcalls` + `ffmpeg` on Railway.\n"
        "- If VC play fails, **no recording is sent anywhere**; only an error message is shown."
    )
    await event.reply(text)

@client.on(events.NewMessage(pattern=r'^\.ping$', outgoing=True, incoming=True))
async def ping_cmd(event):
    start = time.time()
    msg = await event.reply("🏓 Testing...")
    end = time.time()
    await msg.edit(f"🏓 Pong! `{(end - start)*1000:.2f} ms`")

@client.on(events.NewMessage(pattern=r'^\.rules$', outgoing=True, incoming=True))
async def rules_cmd(event):
    text = GROUP_RULES.get(event.chat_id, "No rules set yet.")
    await event.reply(f"📜 **Group Rules:**\n{text}")

# ---------------- ADMIN COMMANDS ----------------
@client.on(events.NewMessage(pattern=r'^\.setrules (.+)$', outgoing=True, incoming=True))
async def set_rules_cmd(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Only admins can set rules.")
    text = event.pattern_match.group(1)
    GROUP_RULES[event.chat_id] = text
    await event.reply("✅ Rules updated.")

@client.on(events.NewMessage(pattern=r'^\.kick(?:\s+(@\w+))?$', outgoing=True, incoming=True))
async def kick_cmd(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Only admins can kick users.")
    arg = event.pattern_match.group(1)
    uid, name = await get_user_from_event(event, arg)
    if not uid:
        return await event.reply("❌ Reply to a user or use @username.")
    try:
        await client.kick_participant(event.chat_id, uid)
        await event.reply(f"✅ Kicked [{name}](tg://user?id={uid})")
    except Exception as e:
        await event.reply(f"❌ Kick failed: {e}")

@client.on(events.NewMessage(pattern=r'^\.ban(?:\s+(@\w+))?$', outgoing=True, incoming=True))
async def ban_cmd(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Only admins can ban users.")
    arg = event.pattern_match.group(1)
    uid, name = await get_user_from_event(event, arg)
    if not uid:
        return await event.reply("❌ Reply to a user or use @username to ban.")
    rights = ChatBannedRights(until_date=None, view_messages=True)
    try:
        await client(EditBannedRequest(event.chat_id, uid, rights))
        await event.reply(f"🚫 Banned [{name}](tg://user?id={uid})")
    except Exception as e:
        await event.reply(f"❌ Ban failed: {e}")

@client.on(events.NewMessage(pattern=r'^\.unban(?:\s+(@\w+))?$', outgoing=True, incoming=True))
async def unban_cmd(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Only admins can unban users.")
    arg = event.pattern_match.group(1)
    uid, name = await get_user_from_event(event, arg)
    if not uid:
        return await event.reply("❌ Reply to a user or use @username to unban.")
    rights = ChatBannedRights(until_date=None, view_messages=False)
    try:
        await client(EditBannedRequest(event.chat_id, uid, rights))
        await event.reply(f"✅ Unbanned [{name}](tg://user?id={uid})")
    except Exception as e:
        await event.reply(f"❌ Unban failed: {e}")

@client.on(events.NewMessage(pattern=r'^\.mute(?:\s+(@\w+))?(?:\s+(\d+)([mhd]))?$', outgoing=True, incoming=True))
async def mute_cmd(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Only admins can mute users.")
    arg, val, unit = event.pattern_match.groups()
    uid, name = await get_user_from_event(event, arg)
    if not uid:
        return await event.reply("❌ Reply or @username required.")

    until_dt = None
    if val and unit:
        val = int(val)
        if unit == "m":
            until_dt = datetime.utcnow() + timedelta(minutes=val)
        elif unit == "h":
            until_dt = datetime.utcnow() + timedelta(hours=val)
        elif unit == "d":
            until_dt = datetime.utcnow() + timedelta(days=val)

    rights = ChatBannedRights(until_date=until_dt, send_messages=True)
    try:
        await client(EditBannedRequest(event.chat_id, uid, rights))
        await event.reply(f"🔇 Muted [{name}](tg://user?id={uid})")
    except Exception as e:
        await event.reply(f"❌ Mute failed: {e}")

@client.on(events.NewMessage(pattern=r'^\.unmute(?:\s+(@\w+))?$', outgoing=True, incoming=True))
async def unmute_cmd(event):
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("❌ Only admins can unmute users.")
    arg = event.pattern_match.group(1)
    uid, name = await get_user_from_event(event, arg)
    if not uid:
        return await event.reply("❌ Reply or @username required.")
    rights = ChatBannedRights(until_date=None, send_messages=False)
    try:
        await client(EditBannedRequest(event.chat_id, uid, rights))
        await event.reply(f"🎙️ Unmuted [{name}](tg://user?id={uid})")
    except Exception as e:
        await event.reply(f"❌ Unmute failed: {e}")

# ---------------- OWNER SPAM WITH UNSCHEDULE ----------------
async def _spam_runner(chat_id: int, interval: float, msg: str, total: int):
    sent = 0
    try:
        while sent < total:
            await client.send_message(chat_id, msg)
            sent += 1
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    finally:
        if chat_id in SCHEDULES:
            del SCHEDULES[chat_id]

@client.on(events.NewMessage(pattern=r'^\.spam\s+([\d.]+)\s+(\d+)\s+(.+)$', outgoing=True, incoming=True))
async def spam_cmd(event):
    if not await is_owner(event.sender_id):
        return await event.reply("❌ Only owner can use `.spam`.")
    interval = float(event.pattern_match.group(1))
    count = int(event.pattern_match.group(2))
    msg = event.pattern_match.group(3)

    if interval < MIN_INTERVAL or interval > MAX_INTERVAL:
        return await event.reply(f"❌ Interval must be between {MIN_INTERVAL}s and {MAX_INTERVAL}s.")
    if count <= 0 or count > MAX_COUNT:
        return await event.reply(f"❌ Count must be between 1 and {MAX_COUNT}.")

    chat_id = event.chat_id
    if chat_id in SCHEDULES:
        SCHEDULES[chat_id].cancel()

    task = asyncio.create_task(_spam_runner(chat_id, interval, msg, count))
    SCHEDULES[chat_id] = task
    await event.reply(f"✅ Spamming `{msg}` every {interval}s × {count}")

@client.on(events.NewMessage(pattern=r'^\.unschedule$', outgoing=True, incoming=True))
async def unschedule_cmd(event):
    if not await is_owner(event.sender_id):
        return await event.reply("❌ Only owner can stop spam.")
    chat_id = event.chat_id
    task = SCHEDULES.get(chat_id)
    if task:
        task.cancel()
        await event.reply("🛑 Spam stopped for this chat.")
    else:
        await event.reply("⚠️ No active spam in this chat.")

# ---------------- OWNER VC CONTROL ----------------
@client.on(events.NewMessage(pattern=r'^\.vcjoin\s+(-?\d+)$', outgoing=True, incoming=True))
async def vcjoin_cmd(event):
    if not await is_owner(event.sender_id):
        return await event.reply("❌ Only owner can set VC target.")
    chat_id = int(event.pattern_match.group(1))
    OWNER_VC_TARGET[event.sender_id] = {"chat_id": chat_id}
    await event.reply(
        f"✅ VC Target set: `{chat_id}`\n"
        f"Example: Reply to a voice note and send `.play`."
    )

@client.on(events.NewMessage(pattern=r'^\.vcleave$', outgoing=True, incoming=True))
async def vcleave_cmd(event):
    if not await is_owner(event.sender_id):
        return await event.reply("❌ Only owner can use this.")
    target = OWNER_VC_TARGET.get(event.sender_id)
    if not target:
        return await event.reply("⚠️ No VC target set. Use `.vcjoin <chat_id>` first.")
    chat_id = target["chat_id"]

    if USE_PYTGCALLS and pytgcalls:
        try:
            await pytgcalls.leave_group_call(chat_id)
        except Exception:
            pass

    del OWNER_VC_TARGET[event.sender_id]
    await event.reply("✅ Left VC and cleared target.")

@client.on(events.NewMessage(pattern=r'^\.play$', outgoing=True, incoming=True))
async def play_cmd(event):
    if not await is_owner(event.sender_id):
        return await event.reply("❌ Only owner can use `.play`.")

    target = OWNER_VC_TARGET.get(event.sender_id)
    if not target:
        return await event.reply("⚠️ Set VC first: `.vcjoin <chat_id>`.")

    if not event.is_reply:
        return await event.reply("❌ Reply to a voice/audio message and then use `.play`.")
    reply = await event.get_reply_message()
    if not (reply.voice or reply.audio or reply.document):
        return await event.reply("❌ Replied message is not a valid audio/voice.")

    chat_id = target["chat_id"]
    await event.reply("⏳ Downloading audio...")
    try:
        temp_path = await client.download_media(reply, file="temp_play_audio")
        if not temp_path or not os.path.exists(temp_path):
            return await event.reply("❌ Download failed.")
    except Exception as e:
        return await event.reply(f"❌ Download error: {e}")

    if USE_PYTGCALLS:
        try:
            await event.reply("▶️ Trying to play in VC...")
            await pytgcalls.join_group_call(chat_id, AudioPiped(temp_path))
            await event.reply("✅ Playing in VC. Use `.vcleave` to stop.")
        except Exception as e:
            await event.reply(
                "⚠️ VC play failed. Check `py-tgcalls`/`ffmpeg` on Railway.\n"
                "🔒 No recording was sent or forwarded anywhere."
            )
    else:
        await event.reply(
            "⚠️ `py-tgcalls` not installed. VC play is disabled.\n"
            "🔒 No recording was sent or forwarded anywhere."
        )

    # हमेशा temp फाइल delete करो
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception:
        pass

# ---------------- DEBUG ----------------
@client.on(events.NewMessage(pattern=r'^\.checkadmin$', outgoing=True, incoming=True))
async def checkadmin_cmd(event):
    is_ad = await is_admin(event.chat_id, event.sender_id)
    await event.reply(f"👑 Admin status here: `{is_ad}`")

# ---------------- MAIN ----------------
async def main():
    global pytgcalls
    await client.start()
    me = await client.get_me()
    print(f"✅ Logged in as {me.first_name} (@{me.username})")

    if USE_PYTGCALLS:
        try:
            pytgcalls = PyTgCalls(client)
            print("🔊 py-tgcalls ready (VC enabled).")
        except Exception as e:
            print(f"⚠️ Failed to init py-tgcalls: {e}")
    else:
        print("⚠️ py-tgcalls not installed, VC play disabled.")

    print("🌹 RoseUserBot v3.1 running on Railway...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())