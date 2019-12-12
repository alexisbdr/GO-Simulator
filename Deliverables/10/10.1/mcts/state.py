from typing import List
from rulechecker import rulecheck, place_stone
from copy import deepcopy
from board import Board, get_all_string_points

class GoGameState():

    def __init__(self, boards:List, stone:str):
        self.board = Board(boards[0])
        self.boards_list = boards
        self.stone = stone
        self.pass_flag1 = False
        self.pass_flag2 = False

    @property
    def game_score(self):
        if not self.pass_flag1 or not self.pass_flag2:
            return None
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
        return self.game_score is not None

    def get_opponent_color(self, stone):
        return "B" if stone == "W" else "W"
    
    def place(self, point):
        if point == "pass":
            if self.pass_flag1: 
                self.pass_flag2 = True
            self.pass_flag1 = True
        new_board = place_stone(self.boards_list[0], self.stone, point)
        new_boards = [new_board] + self.boards_list[:2]
        return GoGameState(new_boards, self.get_opponent_color(self.stone))

    def all_valid_moves(self):
        valid_moves = []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
            if rulecheck(self.boards_list, self.stone, new_point):
                valid_moves.append(new_point)
        if len(valid_moves) <= 1:
            return ["pass"]
        return valid_moves
