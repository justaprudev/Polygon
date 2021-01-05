# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from pathlib import Path

# These functions interact with the database implementation of polygon (polygon.database.Database/polygon.db)
def cache_blacklist() -> dict:
    blacklist = polygon.db.get(NAME)
    if blacklist is None:
        set_blacklist({})
        blacklist = cache_blacklist()
    return blacklist

def get_blacklist(chat_id) -> list:
    blacklist = BLACKLIST_CACHE.get(chat_id, None)
    if blacklist is None:
        BLACKLIST_CACHE[chat_id] = []
        blacklist = []
    return blacklist

def add_blacklist(chat_id, text):
    blacklist = get_blacklist(chat_id)
    if text not in blacklist:
        blacklist.append(text)
        set_blacklist(BLACKLIST_CACHE)
        return True
    return False

def remove_blacklist(chat_id, text):
    blacklist = get_blacklist(chat_id)
    if text in blacklist:
        blacklist.remove(text)
        set_blacklist(BLACKLIST_CACHE)
        return True
    return False

def clear_blacklist(chat_id):
    if chat_id in BLACKLIST_CACHE:
        del BLACKLIST_CACHE[chat_id]
    set_blacklist(BLACKLIST_CACHE)
    return True

def set_blacklist(blacklist: dict):
    polygon.db.add(
        name=NAME,
        value=blacklist
    )

# Constants
NAME = Path(__file__).stem
BLACKLIST_CACHE = cache_blacklist()

@polygon.on(incoming=True)
async def blacklist(e):
    chat_id = str(e.chat_id)
    message = e.text.lower()
    if chat_id in BLACKLIST_CACHE:
        sender = await e.get_sender()
        if not sender: return
        for text in get_blacklist(chat_id):
            if text in message:
                perms = await polygon.get_permissions(int(chat_id), sender)
                if not perms.is_admin:
                    await e.delete()

@polygon.on(pattern="addbl ?(.*)")
async def addblacklist(e):
    chat_id = str(e.chat_id)
    text = e.pattern_match.group(1)
    reply = await e.get_reply_message()
    if not text:
        if reply:
            text = reply.text
    if not text:
        await e.edit("`What do you want to blacklist?`")
        return
    add_blacklist(chat_id, text)
    await e.edit(f"**Blacklisted** `{text}` **in this chat successfully!**")

@polygon.on(pattern="rmbl ?(.*)")
async def removeblacklist(e):
    chat_id = str(e.chat_id)
    text = e.pattern_match.group(1)
    if not text:
        clear_blacklist(chat_id)
        await e.edit("**Cleared the blacklist in this chat successfully!**")
        return
    if remove_blacklist(chat_id, text):
        await e.edit(f"**Removed** `{text}` **from the blacklist in this chat successfully!**")
        return
    await e.edit(f"`{text}` **is not being blacklisted in this chat!**")

@polygon.on(pattern="bl")
async def blacklisted(e):
    chat_id = str(e.chat_id)
    blacklist = get_blacklist(chat_id)
    message = "**Everything blacklisted in this chat:\n**"
    if not blacklist:
        await e.edit("`Nothing has been blacklisted in this chat!`")
        return
    for text in blacklist:
        message += f"\n* `{text}`"
    await e.edit(message)