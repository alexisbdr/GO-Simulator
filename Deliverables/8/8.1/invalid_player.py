from player import AbstractPlayer
from board import Board
import copy
from random import randint
from definitions import *

class InvalidPlayer(AbstractPlayer):
    def make_move(self, boards):
        pass

    def get_suicide_move(self, boards):
        board = Board(boards[0])
        empty_points = board.get_points(" ")
        suicide_points = []
        for point in empty_points:
            board_copy = copy.deepcopy(board)
            board_copy.place(point, self.stone)
            result = board_copy.reachable(point, " ")
            if not result:
                suicide_points.append(point)
        
        if suicide_points:
            choice_index = randint(0, len(suicide_points))
            return suicide_points[choice_index]

        return False

    def get_ko_move(self, boards):
        #get the move that would make this board the same as the second board
        pass

    def get_occupied_move(self, boards):
        board = Board(boards[0])
        opposite_points = board.get_points(self.get_opponent_color())
        choice_index = randint(0, len(opposite_points))
        return opposite_points[choice_index]
        
    
    def get_outofbounds_move(self, boards):
        return str(BOARD_COLUMNS_MAX + 1) + "-" + str(BOARD_COLUMNS_MAX + 1)

