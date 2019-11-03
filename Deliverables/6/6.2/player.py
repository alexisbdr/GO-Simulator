import json
import typing
from typing import List, Union
from copy import deepcopy

from board import Board,get_all_string_points
from rulechecker import makemove, rulecheck
from definitions import *

class Player:

    def __init__(self, name: str, stone: str):
        self.name = name
        self.set_stone(stone)

    #some methods we will need
    def get_name(self) -> str:
        return self.name
    
    def set_stone(self, stone: str):
        if stone not in STONE:
            raise Exception("Invalid Stone in Player")
        self.stone = stone
    
    def get_stone(self):
        if self.stone:
            return self.stone
        else: 
            raise Exception("Player color has not been set")
    
    def make_move(self, Point: str, Boards: List[List]) :
        if rulecheck(Boards, self.get_stone(), Point):
            return makemove(Boards[0], self.get_stone(), Point)
        return None
        

