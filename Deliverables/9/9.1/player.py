import json
import typing
from typing import List, Union
from copy import deepcopy
from board import Board,get_all_string_points
from rulechecker import *
from definitions import *
from utilities import readConfig
from exceptions import PlayerException, StoneException
from abc import ABC, abstractmethod
import random
import copy
#kill $(lsof -t -i:8080)

class AbstractPlayer(ABC):

    def __init__(self):
        self.name = ""
        self.stone = ""
        self.registered = False
        self.ended = False 

    def __eq__(self, other):
        if isinstance(other, AbstractPlayer):
            return self.name == other.name
        return False

    def __hash__(self):
        return id(self)

    def register(self):
        if self.registered:
            raise PlayerException("Player has already been registered")
        self.registered = True
        return self.name
        
    #some methods we will need
    def get_name(self):# -> str:
        if self.registered:
            return self.name
        raise PlayerException("Player has not been registered yet")
    
    def set_stone(self, stone: str):
        if not self.registered:
            raise PlayerException("Player has not been registered yet")
        if stone not in STONE:
            raise StoneException("Invalid Stone in Player")
        self.stone = stone
        self.ended = False

    def receive_stones(self, stone: str):
        self.set_stone(stone)
        return "RECEIVE"
    
    def get_stone(self):
        if self.stone:
            return self.stone
        else: 
            raise StoneException("Player color has not been set")
    
    def get_opponent_color(self):
        return "B" if self.get_stone() == "W" else "W"
    
    def end_game(self):
        if self.ended:
            raise PlayerException("Player has already been notified of game end")
        self.ended = True
        self.stone = ""
        return "OK"
    
    def is_connected(self):
        return False
    
    @abstractmethod
    def make_move(self, boards: List, n: int) -> str:
        pass

class ProxyPlayer(AbstractPlayer):
    
    def _init__(self):
        self.name = ""
        self.stone = ""
        
    def set_conn(self, conn):
        self.conn = conn
        self.client_connected = True
    
    def register(self):
        super().register()
        self.name = self.send(["register"])
        return self.name

    def receive_stones(self, color):
        super().set_stone(color)
        command = ["receive-stones"]
        command.append(color)
        message = json.dumps(command)
        self.conn.sendall(message.encode())
        return

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

    def send(self, message):
        #print("sent message", message)
        try:
            message = json.dumps(message)
            self.conn.sendall(message.encode("UTF-8"))
            resp = self.conn.recv(4096).decode("UTF-8")
            #print("received message", resp)
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
        print(self.name)
    
    def make_move(self, boards: List):
        if not self.strategy: 
            raise Exception("Set Strategy before playing the move")
        self.strategy.apply_strategy(boards, self.get_stone())
