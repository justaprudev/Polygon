import subprocess
from git import Repo
from os import environ
from io import BytesIO
from pathlib import Path
from shutil import rmtree
from functools import wraps
from traceback import format_exc as get_traceback
from importlib.util import module_from_spec, spec_from_file_location

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

def shell(cmd):
    return subprocess.getoutput(cmd)

def wrap_exception(new_exception, *old_exceptions):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except old_exceptions as exc:
                raise new_exception(*exc.args) from None
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

def _execute_module(self):
    try:
        self.__spec__.loader.exec_module(self)
        return True
    except Exception as exception:
        return get_traceback()

def module_from_path(path: Path):
    spec = spec_from_file_location(path.stem, path)  
    module =  module_from_spec(spec)
    setattr(module, "execute", _execute_module.__get__(module))
    return module

def buffer(content:str, name="unnamed", *args):
    buffer = BytesIO(content.encode(), *args)
    buffer.name = name
    return buffer

env = dotdict(environ)