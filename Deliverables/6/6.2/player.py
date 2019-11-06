import json
import typing
from typing import List, Union
from copy import deepcopy

from board import Board,get_all_string_points
from rulechecker import makemove, rulecheck_one, rulecheck_two, rulecheck_three
from definitions import *

class BoardHistory:
    
    def __init__(self, Boards: List[List[str]]):
        self.length = len(Boards)
        if self.length > 3: 
            raise ValueError("Incorrect number of boards in history")
        self.list_of_boards = []
        for board in Boards:
            self.list_of_boards.append(Board(board))
    
    def is_valid(self):
        if self.length == 1: 
            return rulecheck_one(self.list_of_boards, self.stone, self.point)
        if self.length == 2: 
            return rulecheck_two(self.list_of_boards, self.stone, self.point)
        return rulecheck_three(self.list_of_boards, self.stone, self.point)
    
    def add_point(self, Stone: str, Point: str): 
        self.stone = Stone
        self.point = Point
        self.valid_history = self.is_valid()
    
    def make_valid_move(self):
        if self.valid_history:
            new_board = makemove(self.list_of_boards[0], self.stone, self.point)
            return new_board.GetBoard()
        return None
            

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
    
    def move(self, Point: str, Boards: List[List]):
        boardhistory = BoardHistory(Boards)
        boardhistory.add_point(self.get_stone(), Point) 
        return boardhistory.make_valid_move()
        

