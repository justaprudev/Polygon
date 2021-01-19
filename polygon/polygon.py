# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from env import env, SimpleDotDict
from .database import Database
from pathlib import Path
import importlib.util
from os import execl
import nest_asyncio
import telethon
import asyncio
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
        self.db = Database()
        self.modules = {}
        self.env = env
        self.memory = SimpleDotDict()
        self.location = Path(__file__).parent
        self.log = logger   .info
        super().__init__(session, **credentials)
        nest_asyncio.apply(self.loop)
        self.loop.run_until_complete(self._connect())
        self._load(self.location / "__main__.py")
        self.load_from_directory(self.location / "modules")
        self.log(f"Modules loaded: {list(self.modules.keys())}")

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
        self._load(self.location / "modules" / f"{name}.py")
    
    def load_from_directory(self, dirpath):
        for i in Path(dirpath).glob("*.py"):
            self._load(str(i))

    def unload(self, name):
        event_builders = self._event_builders
        for e in event_builders:
            _, callback = e
            if callback.__module__ == name:
                event_builders.remove(e)

        # name = self.modules[shortname].__name__
        # for i in range(len(self._event_builders)):
        #     _, cb = self._event_builders[i]
        #     if cb.__module__ == name:
        #         del self._event_builders[i]
        # del self.modules[shortname]

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
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        self._inject(module)
        # self.modules[shortname] = mod
        spec.loader.exec_module(module)

    def _inject(self, mod):
        mod.polygon = self