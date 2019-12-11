from player import ProxyPlayer
from player import RandomStrategyPlayer
from player_strategy import create_strategy
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
        strategy = create_strategy()
        player = RandomStrategyPlayer()
        player.set_strategy(strategy)
        return player