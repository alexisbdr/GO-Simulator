from player import ProxyPlayer
from player import SimpleValidPlayers 
from player import CapturePlayers
from player import InvalidPlayers, TuringValidPlayer
import importlib.util
from definitions import DEFAULT_PLAYER_CLASS
import random


class PlayerFactory():
    def __init__(self, connection=None, path=None, remote=False):
        self.connection = connection
        self.path = path
        self.remote = remote

    def create(self):
        if self.connection:
            return self.createProxy()
        elif self.path:
            return self.createDefault()
        else:
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
        choice = random.randint(0,2)
        if not choice:
            valid_players = list(all_subclasses(CapturePlayers))
        elif choice == 1: 
            valid_players = list(all_subclasses(SimpleValidPlayers))
        else:
            valid_players = list(all_subclasses(InvalidPlayers))
        choice = random.randint(0, len(valid_players) -1)
        return valid_players[choice]()