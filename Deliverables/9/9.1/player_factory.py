from player import ProxyConnectionPlayer
from player import RandomStrategyPlayer
from player import ProxyStateContractPlayer, ProxyStateContractStrategyPlayer
from player import ProxyTypeContractConnectionPlayer, ProxyTypeContractStrategyPlayer
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
        player = ProxyTypeContractConnectionPlayer(ProxyStateContractPlayer(ProxyConnectionPlayer()))
        player.set_conn(self.connection)
        return player

    def createDefault(self):
        module = __import__(self.path, fromlist=[DEFAULT_PLAYER_CLASS])
        myclass = getattr(module, DEFAULT_PLAYER_CLASS)
        strategy = create_strategy()
        player = ProxyTypeContractStrategyPlayer(ProxyStateContractStrategyPlayer(myclass()))
        player.set_strategy(strategy)
        return player
    
    def createRemote(self):
        strategy = create_strategy()
        player = ProxyTypeContractStrategyPlayer(ProxyStateContractStrategyPlayer(RandomStrategyPlayer()))
        player.set_strategy(strategy)
        return player