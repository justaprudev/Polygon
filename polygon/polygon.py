# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from env import env, SimpleDotDict
from .database import Database
from importlib import util
from pathlib import Path
from git import Repo
from os import execl
import nest_asyncio
import subprocess
import telethon
import asyncio
import shutil
import sys
import re

class Polygon(telethon.TelegramClient):
    def __init__(self, logger, session, **credentials):
        self.name = "Polygon"
        credentials = {
            "device_model": f"Userbot",
            "app_version": f"// {self.name}",
            "lang_code": "en",
            **credentials
        }
        self.path = Path(__file__).parent
        self.module_path = self.path / "modules"
        self.env = env
        self.db = Database()
        self.memory = SimpleDotDict()
        self.log = logger.info
        self.modules = []
        super().__init__(session, **credentials)
        nest_asyncio.apply(self.loop)
        self.loop.run_until_complete(self._connect())
        self._load(self.path / "__main__.py")
        self.load_from_directory(self.module_path)
        self.install_packs()
        self.log(f"Modules loaded: {self.modules}")

    def restart(self):
        execl(sys.executable, sys.executable, *sys.argv)

    def on(self, prefix=".", **kwargs):
        args = kwargs.keys()
        if "forwards" not in args:
            kwargs["forwards"] = False
        if "incoming" not in args:
            kwargs["outgoing"] = True
        if "pattern" in args:
            kwargs["pattern"] = re.compile(f"\\{prefix}" + kwargs["pattern"])
        elif prefix != ".":
            kwargs["pattern"] = re.compile(f"\\{prefix}")
        return super().on(telethon.events.NewMessage(**kwargs))

    def load(self, name):
        name = self._load(self.module_path / f"{name}.py")
        self.modules.append(name)
    
    def load_from_directory(self, dirpath):
        for i in Path(dirpath).glob("*.py"):
            self._load(str(i))
            self.modules.append(i.stem)

    def unload(self, name):
        for callback, _ in self.list_event_handlers():
            if callback.__module__ == name:
                self.remove_event_handler(callback)
                self.modules.remove(name)

    def install_packs(self):
        for i in self.db.get("packs", []):
            pack = i.rsplit('/', 1)[-1].replace(".git", "")
            pack_path = self.module_path / "packs" / pack
            Repo.clone_from(i, pack_path)
            requirements = pack_path / "requirements.txt"
            if requirements.exists():
                for l in open("requirements.txt", "r").read().splitlines():
                    if not l.startswith("#"):
                        subprocess.run(["pip", "install", l])
            try:
                self.load_from_directory(pack_path)
            except:
                self.log(f"Pack {pack} is not supported.")
                shutil.rmtree(pack_path)
        

    async def shell(self, cmd):
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE) 
        stdout, stderr = await proc.communicate()
        return (stdout.decode() or None, stderr.decode() or None)

    async def _connect(self):
        await self.start(bot_token=None)
        self.user = await self.get_me()
        self.log(f"Logged in to {self.user.username or self.user.id}")

    def _load(self, path):
        path = Path(path)
        name = path.stem
        spec = util.spec_from_file_location(name, path)
        module = util.module_from_spec(spec)
        module.polygon = self
        spec.loader.exec_module(module)
        return name