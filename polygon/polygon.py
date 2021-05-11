# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

from logging import root as rootLogger
from polygon import utility, database
from urllib.parse import urlparse
from pathlib import Path
import telethon


class Polygon(telethon.TelegramClient):  # pylint: disable=too-many-ancestors
    def __init__(self, **credentials):
        # Initialization
        self.name = type(self).__name__
        credentials = {
            "device_model": "Userbot",
            "app_version": f"// {self.name}",
            "lang_code": "en",
            **credentials,
        }
        super().__init__(**credentials)

        # Essentials
        self.path = Path(__file__).parent
        self.db = database.Database()
        self.env = utility.env
        self.packages = {}
        self.modules = {}
        self.log = rootLogger.info

        # Extras
        self.shell = utility.shell

        # Load all modules and packages
        self.load_module_from_path(self.path / "__main__.py")
        for module in Path.glob(self.path / "modules", "*.py"):
            self.load_module_from_path(module)
        self.add_packages(*self.db.get("packages", []))
        self.log(f"Modules loaded: {self.modules} \nPackages loaded: {self.packages}")
    
    async def start(self):
        await super().start(bot_token=None)
        self.user = await self.get_me()
        await super().run_until_disconnected()
    
    def run_until_disconnected(self):
        if self.loop.is_running():
            return self.start()
        return self.loop.run_until_complete(self.start())

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
            "blacklist_chats": True,
            "chats": self.db.get("blacklisted_chats"),
            **options,
        }

        prefix = f"\\{prefix}"
        if "pattern" in options:
            options["pattern"] = prefix + options["pattern"]
        elif prefix != "\\.":
            options["pattern"] = prefix

        events = {telethon.events.NewMessage(**options)}
        if edits:
            events.add(telethon.events.MessageEdited(**options))

        def decorator(fn):
            for event in events:
                self.add_event_handler(fn, event)
            return fn

        return decorator

    def load_module_from_path(self, path: Path):
        """Loads a module from it's path.

        Args:
            path (Path): The path of the python module to be loaded.

        Returns:
            [bool]: If the module has been successfully loaded or not.
        """
        module = utility.module_from_path(path)
        utility.setattributes(module, polygon=self, db=self.db, env=self.env, utility=utility)
        return module.execute()
        
    def load_module(self, name: str):
        """Loads a module with just it's name.

        Args:
            name (str): The name of the module to be loaded. Must exist in self.path / 'modules' directory.
        """
        module = self.path / "modules" / f"{name}.py"
        module_supported = self.load_from_path(module)
        if module_supported is not True:
            return self.log(module_supported)
        self.modules[name] = module

    def unload_module(self, name: str, scope: dict = None):
        """Unloads a (loaded) module.

        Args:
            name (str): The name of the module to be unloaded.
        """
        scope = scope or self.modules
        for callback, _ in self.list_event_handlers():
            if callback.__module__ == name:
                self.remove_event_handler(callback)
                del scope[name]

    def add_packages(self, *urls):
        for url in urls:
            self.add_package(url)

    def add_package(self, url: str):
        """Downloads and enables a polygon module package.

        Args:
            url (str): The git url of the polygon module.
        """
        parsed_url = urlparse(url)
        name = Path(parsed_url.path).stem
        package = self.path / "packages" / name

        if package.exists():
            self.remove_package(name)

        utility.gitclone(url, package)
        requirements = package / "requirements.txt"
        if requirements.exists():
            utility.pip(file=requirements)

        package_modules = set()
        for module in package.glob("*.py"):
            module_supported = self.load_module_from_path(module)
            if module_supported is not True:
                # Stop loading modules if any one is unsupported/broken
                # And unload all existing modules of that package
                self.log(f"Package {name} is not supported.")
                self.log(f"Due to:\n{module_supported}")
                self.packages[name] = package_modules
                self.remove_package(name)
                break
            package_modules.add(module)
        self.packages[name] = package_modules
    
    def remove_package(self, name: str):
        """Removes a polygon module package.

        Args:
            name (str): Name of the module package
        """
        package = self.path / "packages" / name
        package_modules = self.packages.get(name, [])
        for module in package_modules:
            self.unload_module(module, self.packages)
        if package.exists():
            utility.rmtree(package)

            

        
