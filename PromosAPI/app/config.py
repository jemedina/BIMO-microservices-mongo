import configparser
import sys 

class GlobalConfiguration:
    def loadConfig(self):
        try:
            configFile = open('app/config/config.cfg','+r')
        except IOError:
            print("Warning: It seems that the config.cfg doesn't exists", file=sys.stderr)
    def __init__(self):
        self.loadConfig()
