# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import io

@polygon.on(prefix="$")
async def shell(e):
    await e.edit("`Evaluating this command..`")
    cmd = e.text[1:]
    reply = await e.get_reply_message()
    stdout, stderr =  await polygon.shell(cmd)
    output = f"**Query:**\n`{cmd}`\n\n**stderr:** \n`{stderr}`\n\n**stdout:**\n`{stdout}`"
    if len(output) > 4096:
        with io.BytesIO(str.encode(output)) as f:
            f.name = "shell.txt"
            await polygon.send_file(
                e.chat_id,
                f,
                force_document=True,
                caption=cmd,
                reply_to=reply
            )
            await e.delete()
            return
    await e.edit(output)