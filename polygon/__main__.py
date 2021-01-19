# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from pathlib import Path

@polygon.on(pattern="load", edits=False)
async def load(e):
    reply = await e.get_reply_message()
    if not reply:
        await e.edit("`Reply to a polygon module to load it.`")
        return
    await e.edit("`Trying to load module..`")
    path = polygon.module_path / reply.file.name
    name = path.stem
    if path.exists():
        await e.edit("`Module already exists, overwriting..`")
        polygon.unload(name)
        path.unlink()
    await polygon.download_media(reply, polygon.module_path)
    try:
        polygon.load(name)
    except Exception as exc:
        await e.edit(f"The following error occured while unloading the module:\n`{exc}`")
        return
    output = f"Loaded module {name} successfully"
    polygon.log(output)
    await e.edit(f"`{output}!`")


@polygon.on(pattern="(un|re)load ?(.*)")
async def load(e):
    module = e.pattern_match.group(2)
    if not module:
        await e.delete()
        return
    path = polygon.module_path / f"{module}.py"
    if not path.exists():
        await e.edit(f"`404: {module} not found!`")
        return
    if e.pattern_match.group(1) == "un":
        if module in polygon.modules:
            polygon.unload(module)
            output = f"Unloaded module {module} successfully"
        else:
            output = f"{module} is not loaded!"
    else:
        if module in polygon.modules:
            polygon.unload(module)
        polygon.load(module)
        output = f"Reloaded module {module} successfully"
    polygon.log(output)
    await e.edit(f"`{output}`")

@polygon.on(pattern="restart")
async def restart(e):
    await e.edit("Polygon will be back soon!\nRun .ping to check if its back.")
    polygon.restart()

@polygon.on(pattern="logs")
async def logs(e):
    await e.edit("`Looking for logs..`")
    if Path("polygon.log").exists():
        await e.respond(file="polygon.log")
        await e.delete()
    else:
        await e.edit("`polygon.log not found!`")