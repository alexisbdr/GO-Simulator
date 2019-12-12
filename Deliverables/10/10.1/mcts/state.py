from typing import List
from rulechecker import rulecheck, place_stone
from copy import deepcopy
from board import Board, get_all_string_points()

class GoGameState():

    def __init__(self, board:List, stone:str):
        self.board = Board(board)
        self.stone = stone

    @property
    def game_score(self):
        score = self.board.count_score()
        score_playerB = score["B"]
        score_playerW = score["W"]

        if score_playerB > score_playerW: 
            return 1
        elif score_playerW > score_playerB: 
            return -1
        else: 
            return 0

    def is_game_over(self):
        #Add some kind of cache in here for precomputed
        return self.game_score()() is not None

    def get_opponent_color(self, stone):
        return "B" if stone == "W" else "W"
    
    def place(self, point):
        return GoGameState(place_stone(self.board), 
            self.stone, point, self.get_opponent_color(stone))

    def all_valid_moves(self):
        valid_moves = []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
            if rulecheck(boards, stone, new_point):
                valid_moves.append(new_point)
        if len(valid_moves) <= 1:
            return ["pass"]
        return valid_moves
