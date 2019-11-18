from player import ProxyPlayer
import importlib.util
from definitions import DEFAULT_PLAYER_CLASS

class PlayerFactory():
    def __init__(self, connection=None, path=None):
        self.connection = connection
        self.path = path
            
    def create(self):
        if self.connection:
            return self.createProxy()
        return self.createDefault()   

    def createProxy(self):
        player = ProxyPlayer()
        player.set_conn(self.connection)
        return player

    def createDefault(self):
        module = __import__(self.path, fromlist=[DEFAULT_PLAYER_CLASS])
        myclass = getattr(module, DEFAULT_PLAYER_CLASS)
        player = myclass()
        #player.set_name("Default Player")
        return player