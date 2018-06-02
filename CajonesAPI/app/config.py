import configparser
import sys 

class GlobalConfiguration:
    def loadConfig(self):
        try:
            configFile = open('app/config/config.cfg','+r')
        except IOError:
            print("Fatal Error: It seems that the config.cfg doesn't exists", file=sys.stderr)
            exit(1)
        config = configparser.ConfigParser()
        config.read_file(configFile)
        try:
            self.DATABASE_HOST = config.get('database','host')
            self.DATABASE_NAME = config.get('database','name')
            self.DATABASE_USER = config.get('database','user')
            self.DATABASE_PASSWD = config.get('database','passwd')
        except Exception:
            print("Fatal Error: File config.cfg must have the database configuration as is in the example file", file=sys.stderr)
            exit(1)
        print("Database configuration loaded successfully")

    def __init__(self):
        self.loadConfig()