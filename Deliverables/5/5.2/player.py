import json
import typing
from typing import List, Union
from copy import deepcopy

from board import Board
from rulechecker import *
from definitions import *

class Player:

    def __init__(self):
        self.name = "no name"
        self.stone = ""

    #some methods we will need
    def get_name(self) -> str:
        return self.name
    
    def set_color(self, stone: str):
        if stone not in STONE:
            raise Exception("Invalid Stone in Player")
        self.stone = stone
    
    def get_color(self):
        if self.stone:
            return self.stone
        else: 
            raise Exception("Player color has not been set")
    
    def make_move(self, boards:List) -> str:
        valid_point = None
        for row in range(BOARD_ROWS_MAX):
            for column in range(BOARD_COLUMNS_MAX):
                new_point = str(row + 1) + "-" + str(column + 1)
                if rulecheck(boards, self.get_color(), new_point):
                    valid_point = new_point if valid_point is None else valid_point
                    check_board = deepcopy(boards[0])
                    if Board(check_board).check_future_liberties(new_point, self.get_color()):
                        return new_point
        if valid_point: return valid_point
        else: return "pass"
    
    
    def update_game_state(self, args):
        raise NotImplementedError
