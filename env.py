class _env():
    def __init__(self):
        import os
        self.__dict__.update(os.environ)

    def __call__(self):
        return self.__dict__

env = _env()