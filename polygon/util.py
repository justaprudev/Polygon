import sys
import asyncio
import subprocess
from os import execl
from pathlib import Path

# Aliases
from traceback import format_exc as get_traceback
from git import Repo
gitclone = Repo.clone_from


def restart():
    execl(sys.executable, sys.executable, *sys.argv)

def setattributes(obj, **attributes):
    for name, value in attributes.items():
        setattr(obj, name, value)

def _pip(package):
    subprocess.run(["pip", "install", package], check=False)

def pip(*packages, file=None):
    for p in packages:
        _pip(p)
    if file:
        if Path(file).exists():
            for l in open(file, "r").readlines():
                _pip(l)

async def blocking_async_shell(cmd):
    proc = await asyncio.create_subprocess_exec(
        *cmd.split(), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return (stdout.decode() or None, stderr.decode() or None)


class dotdict(dict):
    """ A dictionary that allows attribute-style access. """

    def __init__(self, basedict=None, **kwargs):
        """ Creates a new dotdict instance. """
        self.__class__.__getattr__ = self.__getitem__
        self.__class__.__setattr__ = self.__setitem__
        self.__class__.__delattr__ = self.__delitem__
        super().__init__(basedict or {})
        self.update(kwargs)
