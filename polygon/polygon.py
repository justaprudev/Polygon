# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from pathlib import Path
import importlib.util
from os import execl
import sys
import telethon
import nest_asyncio
from polygon import util
from polygon.env import env
from polygon.database import db


class Polygon(telethon.TelegramClient):  # pylint: disable=too-many-ancestors
    def __init__(self, logger, session, **credentials):
        """ Creates a new instance of Polygon and logs in to telegram. """
        self.name = "Polygon"
        credentials = {
            "device_model": "Userbot",
            "app_version": f"// {self.name}",
            "lang_code": "en",
            **credentials,
        }
        super().__init__(session, **credentials)
        nest_asyncio.apply()
        self.start(bot_token=None)
        self.path = Path(__file__).parent
        self.modules = []
        self.log = logger.info
        self.modulepath = self.path / "modules"
        self.shell = util.blocking_async_shell  # temp backwards compatibility
        self.load_from_path(self.path / "__main__.py")
        self.load_from_directory(self.modulepath)
        self.log(f"Modules loaded: {self.modules}")
        # TODO: Add polygon module packages.

    def on(self, edits=True, prefix=".", **options):
        """Custom decorator used to `add_event_handler` more conveniently.

        Args:
            edits (bool, optional): Set to False to disable registration of edits. Defaults to True.
            prefix (str, optional): The prefix to be added before the pattern. Defaults to ".".

        Options:
            incoming (`bool`, optional):
                If set to `True`, only **incoming** messages will be handled.
                Mutually exclusive with ``outgoing`` (can only set one of either).
                Defaults to False.

            outgoing (`bool`, optional):
                If set to `True`, only **outgoing** messages will be handled.
                Mutually exclusive with ``incoming`` (can only set one of either).
                Defaults to True.

            from_users (`entity`, optional):
                Unlike `chats`, this parameter filters the *senders* of the
                message. That is, only messages *sent by these users* will be
                handled. Use `chats` if you want private messages with this/these
                users. `from_users` lets you filter by messages sent by *one or
                more* users across the desired chats (doesn't need a list).

            forwards (`bool`, optional):
                Whether forwarded messages should be handled or not. By default,
                both forwarded and normal messages are included. If it's `True`
                *only* forwards will be handled. If it's `False` only messages
                that are *not* forwards will be handled.
                Defaults to False.

            pattern (`str`, `callable`, `Pattern`, optional):
                If set, only messages matching this pattern will be handled.
                You can specify a regex-like string which will be matched
                against the message, a callable function that returns `True`
                if a message is acceptable, or a compiled regex pattern.
                Defaults to None.
        """
        options = {
            "forwards": False,
            "outgoing": not options.setdefault("incoming", False),
            # TODO: Actually blacklist chats: "blacklist_chats": True,
            "chats": db.get("blacklisted_chats"),
            **options,
        }

        prefix = f"\\{prefix}"
        if "pattern" in options:
            options["pattern"] = prefix + options["pattern"]
        elif prefix != "\\.":
            options["pattern"] = prefix

        events = [telethon.events.NewMessage(**options)]
        if edits:
            events.append(telethon.events.MessageEdited(**options))

        def decorator(fn):
            for event in events:
                self.add_event_handler(fn, event)
            return fn

        return decorator

    def load_from_path(self, path):
        """Loads a specific module from a given path.

        Args:
            path (str): The path of the python module to be loaded.

        Returns:
            [string]: The name of the loaded module.
        """
        path = Path(path)
        name = path.stem
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        util.setattributes(module, polygon=self, db=db, env=env, util=util)
        try:
            spec.loader.exec_module(module)
        except:  # pylint: disable=bare-except
            # Any error in a module must not disrupt the flow of the client.
            self.log(util.get_traceback())
            return False
        return name

    def load_from_directory(self, dirpath):
        """Loads all modules in a specific directory.

        Args:
            dirpath (str): The path of the directory to load modules from.
        """
        for i in Path(dirpath).glob("*.py"):
            self.load_from_path(str(i))
            self.modules.append(i.stem)

    def load(self, name):
        """Loads a module made for polygon.

        Args:
            name (str): The name of the module to be loaded. Must exist in the module directory.
        """
        name = self.load_from_path(self.module_path / f"{name}.py")
        self.modules.append(name)

    def unload(self, name):
        """Unloads a (loaded) module.

        Args:
            name (str): The name of the module to be unloaded.
        """
        for callback, _ in self.list_event_handlers():
            if callback.__module__ == name:
                self.remove_event_handler(callback)
                self.modules.remove(name)

    def restart(self):
        """ Restarts the telegram client. """
        execl(sys.executable, sys.executable, *sys.argv)
