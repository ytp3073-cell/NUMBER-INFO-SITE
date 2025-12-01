# RoseUserBot v3.2 — Render & Railway Ready
# 🔧 Full VC join/play error detection + stable async fixes

import asyncio, time, logging, os
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest, EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantAdmin, ChannelParticipantCreator

# ---------------- CONFIG ----------------
API_ID = int(os.getenv("API_ID", "32581893"))
API_HASH = os.getenv("API_HASH", "86d15530bb76890fbed3453d820e94f5")
SESSION_NAME = os.getenv("SESSION_NAME", "RoseUserBot")

logging.basicConfig(level=logging.WARNING)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ---------------- VC LIB ----------------
USE_PYTGCALLS = False
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types.input_stream import AudioPiped
    USE_PYTGCALLS = True
except Exception as e:
    print(f"⚠️ py-tgcalls not installed or failed: {e}")
    USE_PYTGCALLS = False

pytgcalls = None
OWNER_VC_TARGET = {}
SCHEDULES = {}
GROUP_RULES = {}

MIN_INTERVAL = 0.1
MAX_INTERVAL = 600.0
MAX_COUNT = 10000

# ---------------- ROLE HELPERS ----------------
async def is_owner(uid):
    me = await client.get_me()
    return uid == me.id

async def is_admin(chat_id, uid):
    try:
        part = await client(GetParticipantRequest(chat_id, uid))
        if isinstance(part.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            return True
    except Exception:
        pass
    try:
        perm = await client.get_permissions(chat_id, uid)
        return perm.is_admin or perm.is_creator
    except Exception:
        me = await client.get_me()
        return uid == me.id

async def get_user(event, arg=None):
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.sender:
            return reply.sender_id, reply.sender.first_name
    if arg:
        try:
            u = await client.get_entity(arg)
            name = getattr(u, "first_name", None) or getattr(u, "username", arg)
            return u.id, name
        except:
            return None, None
    return None, None

# ---------------- BASIC ----------------
@client.on(events.NewMessage(pattern=r'^\.start$', outgoing=True, incoming=True))
async def start_cmd(e):
    me = await client.get_me()
    uname = f"@{me.username}" if me.username else me.first_name
    await e.reply(f"🌹 **RoseUserBot v3.2 Active**\n👑 Owner: {uname}\nℹ️ Use `.help` for all commands.")

@client.on(events.NewMessage(pattern=r'^\.help$', outgoing=True, incoming=True))
async def help_cmd(e):
    await e.reply(
        "🌹 **Commands List**\n\n"
        "🧭 Basic: `.start`, `.help`, `.ping`, `.rules`\n"
        "🛡️ Admin: `.setrules`, `.kick`, `.ban`, `.unban`, `.mute`, `.unmute`\n"
        "👑 Owner: `.vcjoin`, `.play`, `.vcleave`, `.spam`, `.unschedule`, `.checkadmin`\n\n"
        "⚠️ VC Notes: Needs `py-tgcalls` + `ffmpeg` installed."
    )

@client.on(events.NewMessage(pattern=r'^\.ping$', outgoing=True, incoming=True))
async def ping_cmd(e):
    start = time.time()
    msg = await e.reply("🏓 Testing...")
    end = time.time()
    await msg.edit(f"🏓 Pong! `{(end - start)*1000:.2f} ms`")

@client.on(events.NewMessage(pattern=r'^\.rules$', outgoing=True, incoming=True))
async def rules_cmd(e):
    await e.reply(f"📜 Rules: {GROUP_RULES.get(e.chat_id, 'No rules set yet.')}")

# ---------------- RULES ADMIN ----------------
@client.on(events.NewMessage(pattern=r'^\.setrules (.+)$', outgoing=True, incoming=True))
async def set_rules(e):
    if not await is_admin(e.chat_id, e.sender_id):
        return await e.reply("❌ Only admins.")
    GROUP_RULES[e.chat_id] = e.pattern_match.group(1)
    await e.reply("✅ Rules updated.")

# ---------------- VC JOIN ----------------
@client.on(events.NewMessage(pattern=r'^\.vcjoin\s+(-?\d+)$', outgoing=True, incoming=True))
async def vcjoin(e):
    if not await is_owner(e.sender_id):
        return await e.reply("❌ Only owner can use this.")
    cid = int(e.pattern_match.group(1))
    OWNER_VC_TARGET[e.sender_id] = {"chat_id": cid}
    await e.reply(f"✅ VC Target set: `{cid}`\n⏳ Checking VC setup...")

    if not USE_PYTGCALLS:
        return await e.reply("⚠️ `py-tgcalls` not installed — VC play disabled.")

    try:
        test = PyTgCalls(client)
        await test.start()
        await e.reply("🔊 py-tgcalls loaded successfully.")
    except Exception as ex:
        return await e.reply(f"❌ py-tgcalls init failed:\n`{ex}`")

    try:
        await test.join_group_call(cid, AudioPiped("test.mp3"))
        await test.leave_group_call(cid)
        await e.reply("✅ VC join success — ready to use `.play`.")
    except Exception as ex:
        await e.reply(f"❌ VC join failed:\n`{ex}`\n💡Check:\n- VC is active\n- Admin rights\n- ffmpeg working")

# ---------------- PLAY AUDIO ----------------
@client.on(events.NewMessage(pattern=r'^\.play$', outgoing=True, incoming=True))
async def play_cmd(e):
    if not await is_owner(e.sender_id):
        return await e.reply("❌ Only owner.")
    t = OWNER_VC_TARGET.get(e.sender_id)
    if not t:
        return await e.reply("⚠️ Set VC first: `.vcjoin <chat_id>`.")
    if not e.is_reply:
        return await e.reply("❌ Reply to a voice/audio message.")
    r = await e.get_reply_message()
    if not (r.voice or r.audio or r.document):
        return await e.reply("❌ Invalid audio message.")
    cid = t["chat_id"]

    await e.reply("⏳ Downloading audio...")
    try:
        path = await client.download_media(r, file="temp_audio.mp3")
        if not path:
            return await e.reply("❌ Download failed.")
    except Exception as ex:
        return await e.reply(f"❌ Download error:\n`{ex}`")

    if not USE_PYTGCALLS:
        return await e.reply("⚠️ `py-tgcalls` not installed, VC disabled.")

    try:
        await e.reply("▶️ Joining VC and playing audio...")
        await pytgcalls.join_group_call(cid, AudioPiped(path))
        await e.reply("✅ Playing in VC.")
    except Exception as ex:
        await e.reply(f"❌ VC play failed:\n`{ex}`\n💡 Ensure VC active, admin + mic permission, ffmpeg installed.")

    try:
        os.remove(path)
    except:
        pass

# ---------------- VC LEAVE ----------------
@client.on(events.NewMessage(pattern=r'^\.vcleave$', outgoing=True, incoming=True))
async def vcleave(e):
    if not await is_owner(e.sender_id):
        return await e.reply("❌ Only owner.")
    t = OWNER_VC_TARGET.get(e.sender_id)
    if not t:
        return await e.reply("⚠️ No VC set.")
    try:
        await pytgcalls.leave_group_call(t["chat_id"])
        await e.reply("✅ Left VC successfully.")
    except Exception as ex:
        await e.reply(f"⚠️ Leave failed: `{ex}`")
    OWNER_VC_TARGET.pop(e.sender_id, None)

# ---------------- DEBUG ----------------
@client.on(events.NewMessage(pattern=r'^\.checkadmin$', outgoing=True, incoming=True))
async def checkadmin_cmd(e):
    a = await is_admin(e.chat_id, e.sender_id)
    await e.reply(f"👑 Admin status: `{a}`")

# ---------------- MAIN ----------------
async def main():
    global pytgcalls
    await client.start()
    me = await client.get_me()
    print(f"✅ Logged in as {me.first_name} (@{me.username})")
    if USE_PYTGCALLS:
        try:
            pytgcalls = PyTgCalls(client)
            await pytgcalls.start()
            print("🔊 py-tgcalls ready.")
        except Exception as e:
            print(f"⚠️ VC init failed: {e}")
    else:
        print("⚠️ py-tgcalls missing, VC disabled.")
    print("🌹 RoseUserBot v3.2 running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())