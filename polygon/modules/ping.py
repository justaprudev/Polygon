# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from datetime import datetime

@polygon.on(pattern="ping")
async def ping(e):
    start = datetime.now()
    await e.edit("Pong!")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await e.edit(f"Pong!\n{ms}")
