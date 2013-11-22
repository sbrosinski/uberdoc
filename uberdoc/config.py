from __future__ import print_function
import sys
from pkg_resources import resource_filename
from os import path

if sys.version_info[0] > 2:
    from configparser import SafeConfigParser

else:
    from ConfigParser import SafeConfigParser

class Config:

    """Encapsulates config file access"""

    def __init__(self, file_name, defaults={}):
        if not path.isfile(file_name):
            file_name = resource_filename(__name__, "uberdoc.cfg")
            if not path.isfile(file_name):
                raise Exception("Can't find config file: " + file_name +
                                " " + path.dirname(path.abspath(__file__)) + " " + os.getcwd())

        self.file_name = file_name
        self.conf = SafeConfigParser(defaults)
        self.conf.readfp(open(file_name))

    def __getitem__(self, key):
        """Shortcut for accessing config options which are handled as
        Config class properties
        """
        try:
            return self.conf.get("MAIN", key)
        except Exception:
            raise Exception(
                "Config file " + self.file_name + " doesn't contain key " + str(key))

    def __setitem__(self, key, value):
        self.conf.set("MAIN", key, value)

    def show(self):
        for key, value in self.conf.items("MAIN"):
            print("  " + key + " = " + value)

    def items(self):
        return self.conf.items("MAIN")

    def user_items(self):
        items = {}
        if "USER" in self.conf.sections():
            for name, value in self.conf.items("USER"):
                items[name] = value
        return items
