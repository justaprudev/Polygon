# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from pathlib import Path

# db functions
def get_gmuted() -> list:
    gmuted_users = db.get(NAME)
    if gmuted_users is None:
        set_gmuted([])
        gmuted_users = get_gmuted()
    return gmuted_users


def is_gmuted(uid):
    if uid in GMUTE_CACHE:
        return True
    return False


def gmute_user(uid):
    if not is_gmuted(uid):
        GMUTE_CACHE.append(uid)
        set_gmuted(GMUTE_CACHE)
        return True
    return False


def ungmute_user(uid):
    if is_gmuted(uid):
        GMUTE_CACHE.remove(uid)
        set_gmuted(GMUTE_CACHE)
        return True
    return False


def set_gmuted(users: list):
    db.add(name=NAME, value=users)


# Constants
NAME = Path(__file__).stem
GMUTE_CACHE = get_gmuted()


@polygon.on(incoming=True, forwards=None)
async def gmute(e):
    sender = await e.get_sender()
    uid = None
    if sender:
        try:
            uid = sender.id
        except AttributeError:
            return
    if is_gmuted(uid):
        await e.delete()


@polygon.on(pattern="gmute ?(.*)")
async def gmuteuser(e):
    user, uid = await get_user(e)
    if uid is None:
        return
    gmuted = gmute_user(uid)
    if gmuted:
        await e.edit(f"**Successfully gmuted** `{user}`")
    else:
        await e.edit(f"`{user}` **is already gmuted!**")


@polygon.on(pattern="ungmute ?(.*)")
async def ungmuteuser(e):
    user, uid = await get_user(e)
    if uid is None:
        return
    ungmuted = ungmute_user(uid)
    if ungmuted:
        await e.edit(f"**Successfully ungmuted** `{user}`")
    else:
        await e.edit(f"`{user}` **was never gmuted!**")


@polygon.on(pattern="listgmute")
async def list_pms(e):
    await e.edit("`Fetching gmuted users..`")
    message = "List of gmuted users:\n"
    if not GMUTE_CACHE:
        await e.edit("`You haven't gmuted anyone!`")
        return
    for i in GMUTE_CACHE:
        message += f"\n* `{i}`"
    message += "\n\ntip: Run .whois <id> to get more info about the users."
    await e.edit(message)


async def get_user(e):
    await e.edit("`...`")
    user = e.pattern_match.group(1)
    reply = await e.get_reply_message()
    if not user:
        try:
            uid = reply.sender.id
            user = f"@{reply.sender.username}" or uid
        except AttributeError:
            await e.edit("`Give me a username/id!`")
            return None, None
    else:
        try:
            try:
                user = int(user)
            except ValueError:
                pass
            sender = await polygon.get_entity(user)
        except ValueError:
            await e.edit(f"`{user}` **user not found!**")
            return None, None
        uid = sender.id
    return user, uid
