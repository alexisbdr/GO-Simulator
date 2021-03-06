from player import ProxyConnectionPlayer
from player import RandomStrategyPlayer
from player import ProxyStateContractPlayer, ProxyStateContractStrategyPlayer
from player import ProxyTypeContractConnectionPlayer, ProxyTypeContractStrategyPlayer
from player_strategy import create_strategy
from player_strategy import MonteCarloStrategy
import importlib.util
from definitions import DEFAULT_PLAYER_CLASS, GUI_PLAYER_CLASS
import random



class PlayerFactory():
    
    def __init__(self, connection=None, path=None, remote=False, gui=False, ai=False):
        self.connection = connection
        self.path = path
        self.remote = remote
        self.gui = gui
        self.ai = ai

    def create(self):
        if self.connection:
            return self.createProxy()
        elif self.path and self.gui:
            return self.createGUI()
        elif self.path:
            return self.createDefault()
        elif self.remote and self.gui and self.path:
            return self.createGUI()
        elif self.ai:
            print("Calling ai")
            return self.createMonteCarloSearch()
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
    
    def createGUI(self):
        module = __import__(self.path, fromlist=[GUI_PLAYER_CLASS])
        myclass = getattr(module, GUI_PLAYER_CLASS)
        player = ProxyTypeContractStrategyPlayer(ProxyStateContractStrategyPlayer(myclass()))
        return player
    
    def createMonteCarloSearch(self):
        print("MAKING STRAT")
        strategy = MonteCarloStrategy()
        player = ProxyTypeContractStrategyPlayer(ProxyStateContractStrategyPlayer(RandomStrategyPlayer()))
        player.set_strategy(strategy)
        return player


    