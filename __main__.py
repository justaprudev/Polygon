# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import git, shutil, pathlib, subprocess, os

github = "https://github.com/justaprudev/polygon"
clone_path = pathlib.Path("/tmp") / "polygon"
git.Repo.clone_from(github, single_branch=True, b=os.environ.get("BRANCH", "userbot"), to_path=clone_path)
shutil.rmtree(clone_path / ".git")
shutil.copytree(clone_path, ".", dirs_exist_ok=True)
for l in open("requirements.txt", "r").read().splitlines():
    if not l.startswith("#"):
        subprocess.run(["pip", "install", l])
shutil.rmtree(clone_path)
import polygon