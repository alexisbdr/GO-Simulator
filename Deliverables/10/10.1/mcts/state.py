from typing import List
from rulechecker import rulecheck, place_stone
from copy import deepcopy
from board import Board, get_all_string_points

class GoGameState():

    def __init__(self, boards:List, stone:str, prev_move: str = ""):
        self.board = Board(boards[0])
        self.boards_list = boards
        self.stone = stone
        self.prev_move = prev_move
        self.game_over = False

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
        return self.game_over

    def get_opponent_color(self, stone):
        return "B" if stone == "W" else "W"
    
    def place(self, point):
        if point == "pass" and prev_move == "pass":
            self.game_over = True
        new_board = place_stone(self.boards_list[0], self.stone, point)
        new_boards = [new_board] + self.boards_list[:2]
        return GoGameState(new_boards, self.get_opponent_color(self.stone), prev_move = point)

    def all_valid_moves(self):
        valid_moves = []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
            if rulecheck(self.boards_list, self.stone, new_point):
                valid_moves.append(new_point)
        if len(valid_moves) <= 1:
            return ["pass"]
        return valid_moves
