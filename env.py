from os import environ

# This is a neat little hack I made for accessing dictionary keys as attributes
class SimpleDotDict(dict):
    def __init__(self, **kwargs):
        self.__class__.__getattr__ = self.__getitem__
        self.__class__.__setattr__ = self.__setitem__
        self.__class__.__delattr__ = self.__delitem__
        self.update(kwargs)

env = SimpleDotDict(**environ)