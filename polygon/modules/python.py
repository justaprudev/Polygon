# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import io
import sys
import asyncio
import traceback
from pathlib import Path
from functools import wraps
from threading import Thread

@polygon.on(prefix=">")
async def python(e):
    await e.edit("`Hmm, nice code..`")
    reply = await e.get_reply_message()
    try:
        code = e.text[1:] or reply.text
    except:
        code = ""
    if not code.strip():
        await e.edit("`No code? no output!`")
        return
    try:
        stdout, stderr = await run_in_thread(code, e)
    except:
        await e.edit(f"**Code**:\n```{code}```\n\n**Error**:\n```{traceback.format_exc()}```")
        return
    output = f"**Code**:\n```{code}```\n\n**stderr**:\n{stderr}\n\n**stdout**:\n```{stdout}```"
    if len(output) > 4096:
        with io.BytesIO(str.encode(output)) as f:
            f.name = "python.txt"
            await polygon.send_file(
                e.chat_id,
                f,
                force_document=True,
                caption=code,
                reply_to=reply
            )
            await e.delete()
            return
    await e.edit(output)

def redirect_console_output(func):
    """ Makes a function always return console output (ignores returned output) """

    def set_out():
        defaults = (sys.stdout, sys.stderr)
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        return defaults

    def reset_out(defaults):
        output = (sys.stdout.getvalue() or None, sys.stderr.getvalue() or None)
        sys.stdout, sys.stderr = defaults
        return output

    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            defaults = set_out()
            await func(*args, **kwargs)
            return reset_out(defaults)
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            defaults = set_out()
            func(*args, **kwargs)
            return reset_out(defaults)
    return wrapper

@redirect_console_output
async def run_in_thread(code, e):
    def sync_wrapper(code, e):
        func = "async_wrapper"
        formatted_code = f"async def {func}(e):" + "".join([f"\n    {l}" for l in code.split("\n")])
        exec(formatted_code)
        polygon.loop.run_until_complete(locals()[func](e))
    thread = Thread(target=sync_wrapper, args=[code, e])
    thread.start()
    five_ms = 5e-3
    while thread.is_alive():
        await asyncio.sleep(five_ms)
