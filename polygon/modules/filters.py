# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from pathlib import Path

# These functions interact with the database implementation of polygon (polygon.database.Database/polygon.db)
def cache_filters() -> dict:
    filters = polygon.db.get(NAME)
    if filters is None:
        set_filters({})
        filters = cache_filters()
    return filters

def get_filters(chat_id) -> dict:
    filters = FILTERS_CACHE.get(chat_id, None)
    if filters is None:
        FILTERS_CACHE[chat_id] = {}
        filters = FILTERS_CACHE[chat_id]
    return filters

def add_filter(chat_id, name, content):
    filters = get_filters(chat_id)
    filters[name] = content
    set_filters(FILTERS_CACHE)
    return True

def remove_filter(chat_id, name):
    filters = get_filters(chat_id)
    if name in filters:
        del filters[name]
        set_filters(FILTERS_CACHE)
        return True
    return False

def clear_filters(chat_id):
    if chat_id in FILTERS_CACHE:
        del FILTERS_CACHE[chat_id]
    set_filters(FILTERS_CACHE)
    return True

def set_filters(filters: dict):
    polygon.db.add(
        name=NAME,
        value=filters
    )

# Constants
NAME = Path(__file__).stem
FILTERS_CACHE = cache_filters()

@polygon.on(incoming=True)
async def filter(e):
    chat_id = str(e.chat_id)
    message = e.text
    if chat_id in FILTERS_CACHE.keys():
        for name, content in get_filters(chat_id).items():
            if name in message:
                if type(content) is int:
                    f = await polygon.get_messages(polygon.user.id, ids=content)
                    await polygon.forward_messages(e.chat_id, f) # Forwarding is fast
                    return
                await e.reply(content)

@polygon.on(pattern="filter ?(.*);+?(.*)")
async def addfilter(e):
    chat_id = str(e.chat_id)
    name = e.pattern_match.group(1)
    content = e.pattern_match.group(2)
    reply = await e.get_reply_message()
    if not name:
        await e.edit("`What do you want to filter?`")
        return
    if not content:
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
            await e.edit("`What do you want to filter it with?`")
            return
    add_filter(chat_id, name, content)
    await e.edit(f"**Started filtering** `{name}` **in this chat successfully!**")

@polygon.on(pattern="stop ?(.*)")
async def removefilter(e):
    chat_id = str(e.chat_id)
    name = e.pattern_match.group(1)
    if not name:
        clear_filters(chat_id)
        await e.edit("**Stopped all filters in this chat successfully!**")
        return
    if remove_filter(chat_id, name):
        await e.edit(f"**Stopped filter** `{name}` in this chat **successfully!**")
        return
    await e.edit(f"`{name}` **is not being filtered in this chat!**")

@polygon.on(pattern="filters")
async def filters(e):
    chat_id = str(e.chat_id)
    filters = get_filters(chat_id)
    message = "**All filters in this chat:\n**"
    if not filters:
        await e.edit("`There are no filters in this chat!`")
        return
    for name in filters:
        message += f"\n* `{name}`"
    await e.edit(message)