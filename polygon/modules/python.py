# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import io
import sys
import asyncio
from functools import wraps
from threading import Thread


@polygon.on(prefix=">")
async def python(e):
    await e.edit("`Hmm, nice code..`")
    reply = await e.get_reply_message()
    try:
        code = e.text[1:] or reply.text
    except (IndexError, AttributeError):
        code = ""
    if not code.strip():
        await e.edit("`No code? no output!`")
        return
    stdout, stderr = await run_in_thread(code, e)
    formatted_stderr = (
        str(stderr)
        .split("__async__wrapper__\n")[-1]  # For errors on runtime.
        .split("exec(formatted_code)\n")[-1]  # For errors while compiling.
        .strip()
    )
    output = (
        f"**Code**:\n```{code}```"
        f"\n\n**stderr**:\n```{formatted_stderr}```"
        f"\n\n**stdout**:\n```{stdout}```"
    )
    if len(output) > 4096:
        with io.BytesIO(output.encode()) as f:
            f.name = "python.txt"
            await polygon.send_file(
                e.chat_id,
                f,
                force_document=True,
                caption=f"```{code}```",
                reply_to=reply,
            )
            await e.delete()
            return
    await e.edit(output)


def redirect_console_output(fn):
    """ Makes a function always return console output (ignores returned output) """

    def set_out():
        defaults = (sys.stdout, sys.stderr)
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        return defaults

    def reset_out(defaults):
        output = (sys.stdout.getvalue() or None, sys.stderr.getvalue() or None)
        sys.stdout, sys.stderr = defaults
        return output

    if asyncio.iscoroutinefunction(fn):

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            defaults = set_out()
            await fn(*args, **kwargs)
            return reset_out(defaults)

    else:

        @wraps(fn)
        def wrapper(*args, **kwargs):
            defaults = set_out()
            fn(*args, **kwargs)
            return reset_out(defaults)

    return wrapper


@redirect_console_output
async def run_in_thread(code, e):
    def sync_wrapper(loop, code, e):
        fn_name = "__async__wrapper__"
        formatted_code = f"async def {fn_name}(e):" + "".join(
            [f"\n {l}" for l in code.split("\n")]
        )
        exec(formatted_code)
        loop.run_until_complete(locals()[fn_name](e))

    thread = Thread(target=sync_wrapper, args=[polygon.loop, code, e])
    thread.start()
    five_ms = 5e-3
    while thread.is_alive():
        await asyncio.sleep(five_ms)
