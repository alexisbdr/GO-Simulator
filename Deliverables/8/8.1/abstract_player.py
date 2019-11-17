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

class AbstractPlayer(ABC):

    def __init__(self):
        self.name = "no name"
        self.stone = ""
        self.load_config()
    
    def load_config(self):
        config = readConfig(PLAYER_CONFIG_PATH)
        self.depth = config[0]

    #some methods we will need
    def get_name(self):# -> str:
        return self.name
    
    def set_stone(self, stone: str):
        if self.stone in STONE:
            raise StoneException("Player is already registered")
        if stone not in STONE:
            raise StoneException("Invalid Stone in Player")
        self.stone = stone
    
    def get_color(self):
        if self.stone:
            return self.stone
        else: 
            raise StoneException("Player color has not been set")
    
    def get_opponent_color(self):
        return "B" if self.get_color() == "W" else "W"
    

    @abstractmethod
    def make_move(self, boards: List, n: int) -> str:
        pass

    def update_game_state(self, args):
        raise NotImplementedError
