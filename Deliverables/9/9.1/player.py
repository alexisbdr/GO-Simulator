import json
import typing
from typing import List, Union
from copy import deepcopy
from board import Board,get_all_string_points,BoardPoint
from rulechecker import *
from definitions import *
from utilities import readConfig
from exceptions import StoneException, PlayerStateViolation, PlayerTypeError
from player_strategy import PlayerStrategy
from abc import ABC, abstractmethod
import random
import copy
from socket import socket
#kill $(lsof -t -i:8080)

class AbstractPlayer(ABC):

    def __init__(self):
        self.name = ""
        self.stone = ""

    def register(self):
        return self.name
        
    #some methods we will need
    def get_name(self):# -> str:
        return self.name

    def receive_stones(self, stone: str):
        if stone not in STONE: 
            raise StoneException("Invalid Stone in Player")
        self.stone = stone
    
    def get_stone(self):
        if self.stone:
            return self.stone
        else: 
            raise StoneException("Player color has not been set")
    
    def get_opponent_color(self):
        return "B" if self.get_stone() == "W" else "W"
    
    def end_game(self):
        self.stone = ""
        return END_GAME_MESSAGE
    
    def is_connected(self):
        return False
    
    @abstractmethod
    def make_move(self, boards: List) -> str:
        pass

    def __eq__(self, other):
        if isinstance(other, AbstractPlayer):
            return self.get_name() == other.get_name()
        return False

    def __hash__(self):
        return id(self)

class ProxyStateContractPlayer(AbstractPlayer):

    def __init__(self, player):
        self.player = player
        self.registered = False
        self.received = False
        self.ended = False
        self.has_strategy = False
        self.client_connected = False

    def register(self):
        if self.registered:
            raise PlayerStateViolation("Player has already been registered")
        self.registered = True
        return self.player.register()
        
    def get_name(self):
        if self.registered:
            return self.player.get_name()
        raise PlayerStateViolation("Player has not been registered yet")
    
    def receive_stones(self, stone: str):
        print("Calling received stones")
        if not self.registered: 
            raise PlayerStateViolation("Player has not been registered yet")
        if self.received: 
            raise PlayerStateViolation("Player has received stones")
        self.received = True
        self.ended = False
        self.player.receive_stones(stone)
    
    def get_stone(self):
        if self.received:
            return self.player.get_stone()
        else: 
            raise StoneException("Player has no stones")
    
    def set_conn(self, connection):
        return self.player.set_conn(connection)

    def is_connected(self): 
        return self.player.is_connected()
    
    def close_connection(self, shutdown):
        self.player.close_connection(shutdown)

    def make_move(self, boards: List):
        if not self.received: 
            raise PlayerStateViolation("Player asked to make a move but has not received stones")
        if self.ended: 
            raise PlayerStateViolation("Player asked to make a move but has already been notified of end game")
        return self.player.make_move(boards)

    def end_game(self):
        print("state : end game")
        if self.ended:
            raise PlayerStateViolation("Player has already been notified of game end")
        self.ended = True
        self.received = False 
        return self.player.end_game()

class ProxyStateContractStrategyPlayer(ProxyStateContractPlayer):

    def __init__(self, player):
        super().__init__(player)
        self.has_strategy = False
    
    def set_strategy(self, strategy: PlayerStrategy):
        if self.has_strategy: 
            raise PlayerStateViolation("Strategy Player has already received a strategy")
        self.has_strategy = True
        self.player.set_strategy(strategy)

class ProxyTypeContractPlayer(AbstractPlayer):
    
    def __init__(self, player):
        self.player = player

    def register(self):
        register_resp = self.player.register()
        if not register_resp is False and not isinstance(register_resp, str):
            raise PlayerTypeError("Player returned a non-string object: {} as it's name".format(register_resp))
        return register_resp
        
    def get_name(self):
        name = self.player.get_name()
        if not isinstance(name, str):
            raise PlayerTypeError("Player returned a non-string object: {} as it's name".format(name))
        return name
    
    def receive_stones(self, stone: str):
        if not isinstance(stone, str):
            raise PlayerTypeError("Player received a non-string object: {} as it's stone".format(stone))
        if stone not in STONE: 
            raise PlayerTypeError("Player received an invalid stone: {}".format(stone))
        self.player.receive_stones(stone)
    
    def get_stone(self):
        stone = self.player.get_stone()
        if not isinstance(stone, str):
            raise PlayerTypeError("Player returned a non-string object: {} as it's stone".format(stone))
        if stone not in STONE:
            raise PlayerTypeError("Player returned the following invalid stone: {} as it's stone".format(stone))
        return stone

    def is_connected(self):
        return self.player.is_connected()

    def make_move(self, boards: List):
        if not isinstance(boards, list):
            raise PlayerTypeError("Player received non-list object: {} for make-a-move".format(boards))
        not_nested_list = any(not isinstance(b, list) for b in boards)
        if not_nested_list: 
            raise PlayerTypeError("Player should received a nested list object: {} in make-a-move".format(boards))
        return self.player.make_move(boards)

    def end_game(self):
        end_game_resp = self.player.end_game()
        print("type : end game")
        if not isinstance(end_game_resp, str):
            raise PlayerTypeError("Player returned a non-string object as it's end game message: {}".format(end_game_resp))
        return end_game_resp

class ProxyTypeContractConnectionPlayer(ProxyTypeContractPlayer):

    def __init__(self, player):
        super().__init__(player)
        self.player = player
    
    def set_conn(self, connection):
        if not isinstance(connection, socket):
            raise PlayerTypeError("Proxy Connection Player received a non socket object: {} as a connection".format(connection))
        self.player.set_conn(connection)
  
    def close_connection(self, shutdown):
        if not isinstance(shutdown, bool):
            raise PlayerTypeError("Proxy Player shutdown flag should be a boolean, instead: {}".format(shutdown))
        self.player.close_connection(shutdown)

class ProxyTypeContractStrategyPlayer(ProxyTypeContractPlayer):

    def __init__(self, player):
        super().__init__(player)
        self.player = player
    
    def set_strategy(self, strategy):
        if not isinstance(strategy, PlayerStrategy):
            raise PlayerTypeError("Strategy Player received a non strategy object: {} as a strategy".format(strategy))
        self.player.set_strategy(strategy)
    
class ProxyConnectionPlayer(AbstractPlayer):
    
    def _init__(self):
        self.name = ""
        self.stone = ""
        self.client_connected = False
        
    def set_conn(self, conn):
        self.conn = conn
        self.client_connected = True
    
    def register(self):
        super().register()
        self.name = self.send(["register"])
        return self.name

    def receive_stones(self, stone: str):
        super().receive_stones(stone)
        command = ["receive-stones"]
        command.append(stone)
        message = json.dumps(command)
        self.conn.sendall(message.encode())

    def make_move(self, boards):
        command = ["make-a-move"]
        command.append(boards)
        result = self.send(command)
        return result
    
    def end_game(self):
        command = ["end-game"]
        result = self.send(command)
        return result
    
    def is_connected(self):
        return self.client_connected
    
    def close_connection(self, shutdown: bool):
        if shutdown: 
            self.conn.shutdown(1)
        self.conn.close()

    def send(self, message):
        print("sent message", message)
        try:
            message = json.dumps(message)
            self.conn.sendall(message.encode("UTF-8"))
            resp = self.conn.recv(4096).decode("UTF-8")
            print("received message", resp)
            if not resp:
                self.client_connected = False
                return False
            return resp
        except BrokenPipeError:
            print("remote player not connected")
            #self.client_connected = False
            return False

class RandomStrategyPlayer(AbstractPlayer):
    """
    Accepts a strategy and asks it to play
    """
    def __init__(self):
        super().__init__()
        self.strategy = None
    
    def set_strategy(self, strategy):
        self.strategy = strategy
        self.name = strategy.__class__.__name__
    
    def make_move(self, boards: List):
        return self.strategy.apply_strategy(boards, self.get_stone())


