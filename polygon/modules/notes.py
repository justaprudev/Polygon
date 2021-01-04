# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from pathlib import Path

# These functions interact with the database implementation of polygon (polygon.database.Database/polygon.db)
def get_notes() -> dict:
    notes = polygon.db.get(NAME)
    if notes is None:
        set_notes({})
        notes = get_notes()
    return notes

def get_note(name):
    return NOTES_CACHE.get(name, None)

def add_note(name, content):
    NOTES_CACHE[name] = content
    set_notes(NOTES_CACHE)
    return True

def remove_note(name):
    if name in NOTES_CACHE:
        del NOTES_CACHE[name]
        set_notes(NOTES_CACHE)
        return True
    return False

def clear_notes():
    set_notes({})
    NOTES_CACHE.clear()
    return True

def set_notes(notes: dict):
    polygon.db.add(
        name=NAME,
        value=notes
    )

# Constants
NAME = Path(__file__).stem
NOTES_CACHE = get_notes()


@polygon.on(prefix="#")
async def getnote(e):
    name = e.text[1:]
    content = get_note(name)
    if not name:
        return
    if content:
        if type(content) is int:
            await e.edit("`Fetching file..`")
            f = await polygon.get_messages(polygon.user.id, ids=content)
            await polygon.forward_messages(e.chat_id, f) # Forwarding is fast
            await e.delete()
            return
        await e.respond(content)
        await e.delete()
        return
    await e.edit(f"**Note** `{name}` **not found!**")

@polygon.on(pattern="save ?(.*)")
async def addnote(e):
    msg = e.pattern_match.group(1).split(maxsplit=1)
    reply = await e.get_reply_message()
    try: name = msg[0]
    except:
        await e.edit("`You need to give the note a name!`")
        return
    try: content = msg[1]
    except:
        if reply:
            if reply.media:
                await e.edit("`Saving file..`")
                f = await polygon.forward_messages(polygon.user.id, reply) # Forwarding is fast
                content = int(f.id)
                await f.reply(
                    f"`[DO NOT DELETE]`\
                    \n**This file was saved by polygon**\
                    \n**name:** `{name}`\
                    \n**id:** `{content}`"
                )
            else:
                content = reply.text
        else:
            await e.edit("`You need provide content for the note!`")
            return
    add_note(name, content)
    await e.edit(f"**Saved note** `{name}` **successfully!**")

@polygon.on(pattern="clear ?(.*)")
async def removenote(e):
    try: name = e.pattern_match.group(1).split(maxsplit=1)[0]
    except:
        clear_notes()
        await e.edit("**Cleared all personal notes successfully!**")
        return
    if remove_note(name):
        await e.edit(f"**Removed note** `{name}` **successfully!**")
        return
    await e.edit(f"**Note** `{name}` **doesn't exist!**")

@polygon.on(pattern="notes")
async def notes(e):
    message = "**Your personal notes:\n**"
    if not NOTES_CACHE:
        await e.edit("`You have saved no personal notes!`")
        return
    for name in NOTES_CACHE:
        message += f"\n* `{name}`"
    message += "\n\n**Tip: Use #notename to get the contents of the note.**"
    await e.edit(message)