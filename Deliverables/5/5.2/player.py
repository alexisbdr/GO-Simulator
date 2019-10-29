import json
import typing
from typing import List, Union
from copy import deepcopy

from board import Board,get_all_string_points
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
    
    def get_opponent_color(self):
        return "B" if self.get_color() == "W" else "W"

    def all_valid_moves(self, boards: List, stone: str) -> List[str]:
        """
        Returns a list of valid moves for a given board history and stone
        """
        valid_moves, valid_capture_moves = [], []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
                if rulecheck(boards, stone, new_point):
                    valid_moves.append(new_point)
                    if self.make_move_capture_two(boards, new_point):
                        valid_capture_moves.append(new_point)
        return valid_moves, valid_capture_moves

    def make_move(self, boards: List, n: int) -> str:
        """
        Determines the make-move strategy based on the parameter n
        Returns: 
            -"pass" if there are no valid moves
            -first valid point by column-row order
            -first valid point that leads to a capture of the opponent
            -first valid point of a sequence of moves that lead to a capture
        """
        if n > 1:
            result = self.make_move_two(boards, n)
            if result:
                return result
        
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_color())
        #If list is empty then there are no valid moves
        if not valid_moves: 
            return PASS_OUTPUT
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

        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_color())
        if len(boards) == 1 or len(boards) == 2:
            return valid_moves[0]

        if n == 1 and valid_capture_moves:
            return valid_capture_moves[0]
        elif n == 1 and valid_moves:
            return valid_moves[0]
        elif n > 1:
            capture = self.make_move_recursive([], boards, n) # or call make_move_points_of_interest here
            if capture:
                return capture
            elif valid_moves:
                return valid_moves[0]
            else:
                return PASS_OUTPUT
        else:
            return PASS_OUTPUT

    def make_move_points_of_interest(self, boards: List, n: int) -> str:

        boards = deepcopy(boards)
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_color())
        for move in valid_moves:
            new_board = makemove(boards[0], self.get_color(), move)
            new_boards = [new_board, boards[0], boards[1]]
            valid_opponent_moves, valid_opponent_capture_moves = \
                self.all_valid_moves(new_boards, self.get_opponent_color())
            leads_to_capture = True
            for opponent_move in valid_opponent_moves:
                if opponent_move in valid_opponent_capture_moves or \
                        opponent_move in valid_capture_moves:
                    new_board2 = makemove(new_board, self.get_opponent_color(), opponent_move)
                    new_boards = [new_board2, new_board, boards[0]]
                    new_valid_moves, new_valid_capture_moves = \
                        self.all_valid_moves(new_boards, self.get_color())
                    if not new_valid_capture_moves:
                        leads_to_capture = False
            if leads_to_capture:
                return move
        return valid_moves[0]

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
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_color())
        opposite_stone = self.get_opponent_color()
        if n == 1: # if n == 1, we need to make a capture right away
            if self.make_move_capture(boards, valid_moves):
                return list_of_moves[0]
            else:
                return None
        for move in valid_moves:
            list_of_moves.append(move)
            if self.make_move_capture(boards, [move]):
                return list_of_moves[0]
            new_board = makemove(boards[0], self.get_color(), move)
            valid_opponent_moves, valid_opponent_capture_moves = self.all_valid_moves([new_board, boards[0], boards[1]], opposite_stone)
            leads_to_capture = True
            for opponent_move in valid_opponent_moves:
                #if opponent_move in valid_opponent_capture_moves or \
                #        opponent_move in valid_capture_moves: <-- tried adding this, didn't work for some reason
                ## but I will try debugging
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
