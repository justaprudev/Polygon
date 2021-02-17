import traceback
import asyncio

get_traceback = traceback.format_exc


def setattributes(module, **attributes):
    for name, value in attributes.items():
        setattr(module, name, value)


# def install_packs(self):
#     for i in self.db.get("packs", []):
#         pack = i.rsplit("/", 1)[-1].replace(".git", "")
#         pack_path = self.module_path / "packs" / pack
#         if pack_path.exists():
#             shutil.rmtree(pack_path)
#         Repo.clone_from(i, pack_path)
#         requirements = pack_path / "requirements.txt"
#         if requirements.exists():
#             for l in open(requirements, "r").read().splitlines():
#                 if not l.startswith("#"):
#                     subprocess.run(["pip", "install", l])
#         try:
#             self.load_from_directory(pack_path)
#         except:
#             self.log(f"Pack {pack} is not supported.")
#             shutil.rmtree(pack_path)


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
