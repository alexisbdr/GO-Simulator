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

    def all_valid_moves(self, boards: List, stone: str) -> List[str]:
        """
        Returns a list of valid moves for a given board history and stone
        """
        valid_moves = []
        for row in range(BOARD_ROWS_MAX):
            for column in range(BOARD_COLUMNS_MAX):
                new_point = str(row + 1) + "-" + str(column + 1)
                if rulecheck(boards, stone, new_point):
                    valid_moves.append(new_point)
        return valid_moves

    def make_move(self, boards: List, n: int) -> str:
        """
        Determines the make-move strategy based on the parameter n
        Returns: 
            -"pass" if there are no valid moves
            -first valid point by column-row order
            -first valid point that leads to a capture of the opponent
            -first valid point of a sequence of moves that lead to a capture
        """
        if len(boards) == 1 or len(boards) == 2:
            valid_moves = self.all_valid_moves(boards, self.get_color())
            return valid_moves[0]

        if n > 1:
            result = self.make_move_recursive([], boards, n)
            if result:
                return result
        
        valid_moves = self.all_valid_moves(boards, self.get_color())
        #If list is empty then there are no valid moves
        if not valid_moves: 
            return "pass"
        capture_point = self.make_move_capture(boards, valid_moves)
        #If no moves lead to an opponent capture - return first valid point
        if not capture_point:
            return valid_moves[0]
        return capture_point
    
    def make_move_capture(self, boards:List, valid_moves:List[str]) -> Union[bool, str]:
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise 
        """
        boards = deepcopy(boards)
        for point in valid_moves: 
            if Board(boards[0]).check_future_liberties(point, self.get_color()):
                return point
        return False

    def make_move_capture_two(self, boards:List, point: str) -> Union[bool, str]:
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise
        """
        boards = deepcopy(boards)
        if Board(boards[0]).check_future_liberties(point, self.get_color()):
            return True
        return False

    def make_move_two(self, boards: List, n: int):
        valid_moves = self.all_valid_moves(boards, self.get_color())
        capture_moves = []
        for move in valid_moves:
            if self.make_move_capture_two(boards, move):
                capture_moves.append(move)
        if len(capture_moves) >= n:
            return valid_moves[0]
        else:
            return capture_moves[0]

    def make_move_recursive(self, list_of_moves: List, boards:List, n: int) -> str:
        """
        Steps: 
            1.Finds and iterates through valid player moves
            2.For each valid player move 
            3.Find and iterate through valid opponent moves
            4.Make valid opponent move
            5.Call self recursive move on new update board state after player and opponent valid moves
        """
        boards = deepcopy(boards)
        valid_moves = self.all_valid_moves(boards, self.get_color())
        if n == 1:
            if self.make_move_capture(boards, valid_moves):
                return list_of_moves[0]
            else:
                return None
        opposite_stone = "B" if self.get_color() == "W" else "W"
        for move in valid_moves:
            list_of_moves.append(move)
            if self.make_move_capture(boards, [move]):
                return list_of_moves[0]
            new_board = makemove(boards[0], self.get_color(), move)
            valid_opponent_moves = self.all_valid_moves([new_board, boards[0], boards[1]], opposite_stone)
            leads_to_capture = True
            for opponent_move in valid_opponent_moves:
                new_board2 = makemove(new_board, opposite_stone, opponent_move)
                result = self.make_move_recursive(list_of_moves, [new_board2, new_board, boards[0]], n-1)
                if result is None:
                    leads_to_capture = False
                    break
                else:
                    continue
            if leads_to_capture:
                return list_of_moves[0]
            list_of_moves.pop()
        return None

    def update_game_state(self, args):
        raise NotImplementedError
