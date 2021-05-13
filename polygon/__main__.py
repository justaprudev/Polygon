# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev
from pathlib import Path

@polygon.on(pattern="load")
async def load(e):
    reply = await e.get_reply_message()
    if not reply:
        return await e.edit("`Reply to a polygon module to load it.`")

    await e.edit("`Trying to load module..`")
    path = polygon.path / "modules" / reply.file.name
    name = path.stem
    
    if path.exists():
        await e.edit("`Module already exists, overwriting..`")
        polygon.unload_module(name)
        path.unlink()
        
    await polygon.download_media(reply, path.parent)
    polygon.load_module(name)
    await e.edit(f"`Loaded module {name} successfully!`")


@polygon.on(pattern="(un|re)load ?(.*)")
async def unload_and_reload(e):
    module = e.pattern_match.group(2)
    path = polygon.modules.get(module)
    if not path:
        return await e.delete()
    elif not path.exists():
        return await e.edit(f"`404: {module} not found!`")
    
    if e.pattern_match.group(1) == "un":
        if module in polygon.modules:
            polygon.unload_module(module)
            output = f"Unloaded module {module} successfully"
        else:
            output = f"{module} is not loaded!"
    else:
        if module in polygon.modules:
            polygon.unload_module(module)
        polygon.load_module(module)
        output = f"Reloaded module {module} successfully"

    await e.edit(f"`{output}`")


@polygon.on(pattern="restart")
async def restart(e):
    await e.edit("Polygon will be back soon!\nRun .ping to check if its back.")
    polygon.restart()


@polygon.on(pattern="logs")
async def logs(e):
    log = Path("polygon.log")
    await e.edit("`Looking for logs..`")
    if log.exists():
        # We need to reverse the logs in order to show the lastest first
        reversed_logs = "".join(reversed(open(log, "r").readlines()))
        await e.respond(file=utility.buffer(reversed_logs, log.name))
        await e.delete()
    else:
        await e.edit("`Enable to find logfile [polygon.log].`")
