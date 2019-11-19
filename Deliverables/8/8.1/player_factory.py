from player import ProxyPlayer, SimpleValidPlayers, CapturePlayers
import importlib.util
from definitions import DEFAULT_PLAYER_CLASS
import random


class PlayerFactory():
    def __init__(self, connection=None, path=None, player_cls=None):
        self.connection = connection
        self.path = path
        self.player_cls = player_cls

    def create(self):
        if self.connection:
            return self.createProxy()
        elif self.path:
            return self.createDefault()
        return self.createRemote()

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
    
    def createRemote(self):
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in all_subclasses(c)]) 
        valid_players = all_subclasses(self.player_cls)
        choice = random.randint(0, len(valid_players) -1)
        return valid_players[choice]()