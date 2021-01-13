import re
import asyncio
from os import kill
from pathlib import Path
from signal import SIGTERM
from pymegatools import Megatools

megatools = Megatools()
dldir = Path("mega")

@polygon.on(pattern="mega -k ?(.*)")
async def megakill(e):
	dl_not_found = "`Download not found. (Invalid PID)`"
	try: pid = int(e.pattern_match.group(1))
	except:
		await e.edit(dl_not_found)
		return
	try: kill(pid, SIGTERM)
	except: await e.edit(dl_not_found)
	else: await e.edit(f"`Successfully killed download with pid {pid}`")
	
	
@polygon.on(pattern="mega ?(.*)")
async def mega(e):
    if not dldir.exists():
        dldir.mkdir()
    url = e.pattern_match.group(1)
    if not url:
        await e.edit(f"`{megatools.version()}`")
        return
    if url.startswith("-k"): return
    await e.edit("`Trying to download..`")
    filename = megatools.filename(url)
    stdout, exit_code = megatools.download(url, callback_wrapper, [e], path=dldir.name)
    if exit_code == 0:
        output = f"Downloaded {filename}" if filename else "Invalid URL."
    elif exit_code == 1:
        output = "File already exists!\nCheck the mega folder."
    elif exit_code == -15:
    	output = f"Download for {filename} was cancelled."
    else:
        output = f"Whoops! Something went wrong, Exit code: {exit_code}"
    try: await e.edit(f"`{output}`")
    except: pass

def callback_wrapper(proc, e):
    async def callback(proc, e):
        output = proc.stdout.readline()
        if output:
            match = re.match("(.*): (.*) - (.*) \(.*\) of (.*) \((.*)\)", output.decode())
            if match:
                await e.edit(
                f"**Downloading:** `{match.group(1)}`\
                \n**Progress:** `{match.group(2)}`\
                \n**Downloaded:** `{match.group(3)}`\
                \n**Total Size:** `{match.group(4)}`\
                \n**Speed:** `{match.group(5)}`\
                \n**PID:** `{proc.pid}`\
                \n\n"
                )
        await asyncio.sleep(1)
    polygon.loop.run_until_complete(callback(proc=proc, e=e)) # nest_asyncio
