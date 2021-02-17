# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import re
from pathlib import Path
from telethon.tl import functions

# db functions
def get_approved() -> list:
    approved_users = db.get(NAME)
    if not approved_users:
        set_approved([777000, polygon.user.id])
        approved_users = get_approved()
    return approved_users


def is_approved(uid):
    if uid in APPROVED_CACHE:
        return True
    return False


def approve(uid):
    if not is_approved(uid):
        APPROVED_CACHE.append(uid)
        set_approved(APPROVED_CACHE)
        return True
    return False


def disapprove(uid):
    if is_approved(uid):
        APPROVED_CACHE.remove(uid)
        set_approved(APPROVED_CACHE)
        return True
    return False


def set_approved(users: list):
    db.add(name=NAME, value=users)


# Constants
PM_WARNS = {}
PREVIOUS_MESSAGES = {}
NAME = Path(__file__).stem
APPROVED_CACHE = get_approved()
BLOCK_MESSAGE = "```Blocked! Thanks for the spam.```"
WARNING_MESSAGE = "\
```Bleep blop! This is a bot. Don't fret.\
\nMy master hasn't approved you to PM.\
\nPlease wait for my master to look in, he mostly approves PMs.\
\nAs far as I know, he doesn't usually approve retards though.\
\nIf you continue sending messages you will be blocked.```\
"


@polygon.on(incoming=True, func=lambda e: e.is_private, forwards=None)
async def antispam(e):
    uid = e.chat_id
    sender = await e.get_sender()
    try:
        if sender.bot:
            return
    except AttributeError:
        pass
    approved = is_approved(uid)
    if not approved:
        if uid not in PM_WARNS:
            PM_WARNS.update({uid: 0})
        if PM_WARNS[uid] == 5:
            response = await e.reply(BLOCK_MESSAGE)
            await PREVIOUS_MESSAGES[uid].delete()
            await polygon(functions.contacts.BlockRequest(uid))
            del PREVIOUS_MESSAGES[uid]
            del PM_WARNS[uid]
            return
        response = await e.reply(
            f"{WARNING_MESSAGE}\n`Messages remaining: {int(5 - PM_WARNS[uid])} out of 5`"
        )
        PM_WARNS[uid] += 1
        if uid in PREVIOUS_MESSAGES:
            await PREVIOUS_MESSAGES[uid].delete()
        PREVIOUS_MESSAGES[uid] = response


@polygon.on(outgoing=True, func=lambda e: e.is_private)
async def autoapprove(e):
    uid = e.chat_id
    if not is_approved(uid):
        if not re.match("^(.)disapprove$", e.text) and not re.match(
            "^(.)approve$", e.text
        ):
            approve(uid)


@polygon.on(pattern="approve", func=lambda e: e.is_private)
async def approve_pm(e):
    await e.edit("`...`")
    uid = e.chat_id
    approved = approve(uid)
    if approved:
        await e.edit("`Approved PM.`")
        if PM_WARNS.get(uid):
            del PM_WARNS[uid]
        if PREVIOUS_MESSAGES.get(uid):
            del PREVIOUS_MESSAGES[uid]
    else:
        await e.edit("`This user is already approved!`")


@polygon.on(pattern="disapprove", func=lambda e: e.is_private)
async def disapprove_pm(e):
    await e.edit("`...`")
    uid = e.chat_id
    disapproved = disapprove(uid)
    if disapproved:
        await e.edit("`Disapproved PM.`")
    else:
        await e.edit("`This user isnt approved!`")


@polygon.on(pattern="listpms")
async def list_pms(e):
    await e.edit("`Fetching approved users..`")
    approved_users = APPROVED_CACHE[2:]
    message = "List of approved users:\n"
    if not approved_users:
        await e.edit("`You haven't approved anyone!`")
        return
    for i in approved_users:
        message += f"\n* `{i}`"
    message += "\n\ntip: Run .whois <id> to get more info about the users."
    await e.edit(message)
