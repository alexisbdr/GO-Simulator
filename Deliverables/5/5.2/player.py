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
                    if Board(boards[0]).check_future_liberties(new_point, self.get_color()):
                        return new_point
        if valid_point: return valid_point
        else: return "pass"

    def all_valid_moves(self, boards: List, stone: str) -> List[str]:
        valid_moves = []
        for row in range(BOARD_ROWS_MAX):
            for column in range(BOARD_COLUMNS_MAX):
                new_point = str(row + 1) + "-" + str(column + 1)
                if rulecheck(boards, stone, new_point):
                    valid_moves.append(new_point)
        return valid_moves

    def make_move_2(self, boards:List) -> str:
        valid_moves = self.all_valid_moves(boards, self.get_color()) ## get all possible moves
        opposite_stone = "B" if self.get_color() == "W" else "W"
        for move in valid_moves:
            new_board = makemove(boards[0], self.get_color(), move)
            valid_opponent_moves = self.all_valid_moves(self, [new_board, boards[0], boards[1]], opposite_stone)
            all_moves_lead_to_capture = True
            for opponent_move in valid_opponent_moves:
                new_board2 = makemove(new_board, opposite_stone, opponent_move)
                if not self.make_move([new_board2, new_board, boards[0]]): ## change so that it returns false if we cant capture right away
                    all_moves_lead_to_capture = False
            if all_moves_lead_to_capture:
                return move
        return --
    
    
    def update_game_state(self, args):
        raise NotImplementedError
