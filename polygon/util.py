import asyncio
import subprocess
from pathlib import Path
from functools import wraps

# Aliases
from traceback import format_exc as get_traceback
from git import Repo
gitclone = Repo.clone_from

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
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return (stdout.decode() or None, stderr.decode() or None)

def wrap_exception(new_exception, *old_exceptions):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except old_exceptions as exc:
                raise exception(*exc.args) from None
        return wrapper
    return decorator


class dotdict(dict):
    """ A dictionary that allows attribute-style access. """

    def __init__(self, basedict=None, **kwargs):
        """ Creates a new dotdict instance. """
        super().__init__(basedict or {})
        self.update(kwargs)

    @wrap_exception(AttributeError, KeyError)
    def __getattr__(self, *args, **kwargs):
        return super().__getitem__(*args, **kwargs)

    @wrap_exception(AttributeError, KeyError)
    def __setattr__(self, *args, **kwargs):
        return super().__setitem__(*args, **kwargs)

    @wrap_exception(AttributeError, KeyError)
    def __delattr__(self, *args, **kwargs):
        return super().__delitem__(*args, **kwargs)
