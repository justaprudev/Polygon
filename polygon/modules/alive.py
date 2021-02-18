# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev


@polygon.on(pattern="alive", edits=True)
async def alive(e):
    reply = await e.get_reply_message()
    await e.edit("`Fetching information..`")
    caption = (
        "**// Polygon is running //**"
        f"\n\n`User:` [{polygon.user.first_name or 'Unknown'} {polygon.user.last_name or ''}](tg://user?id={polygon.user.id})"
        "\n`Github:` justaprudev.github.io/polygon"
        "\n`Build: v0.5 (beta)`"
        "\n\n**By** @justaprudev"
    )
    await polygon.send_file(
        e.chat_id,
        caption=caption,
        file="https://telegra.ph/file/c36a71456ba76f827274c.jpg",
        force_document=False,
        reply_to=reply,
    )
    await e.delete()
