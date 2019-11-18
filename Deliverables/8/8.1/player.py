import json
import typing
from typing import List, Union
from copy import deepcopy
from board import Board,get_all_string_points
from rulechecker import *
from definitions import *
from utilities import readConfig
from exceptions import PlayerException, StoneException
from abc import ABC, abstractmethod
import random

class AbstractPlayer(ABC):

    def __init__(self):
        self.name = "no name"
        self.stone = ""
        self.load_config()
    
    def load_config(self):
        config = readConfig(PLAYER_CONFIG_PATH)
        self.depth = config[0]

    def set_name(self, name: str):
        self.name = name

    #some methods we will need
    def get_name(self):# -> str:
        return self.name
    
    def set_stone(self, stone: str):
        if self.stone in STONE:
            raise StoneException("Player is already registered")
        if stone not in STONE:
            raise StoneException("Invalid Stone in Player")
        self.stone = stone
    
    def get_stone(self):
        if self.stone:
            return self.stone
        else: 
            raise StoneException("Player color has not been set")
    
    def get_opponent_color(self):
        return "B" if self.get_stone() == "W" else "W"
    

    @abstractmethod
    def make_move(self, boards: List, n: int) -> str:
        pass

    def update_game_state(self, args):
        raise NotImplementedError



class ProxyPlayer(AbstractPlayer):
    
    def _init__(self):
        self.name = ""
        self.stone = ""

    def set_conn(self, conn):
        self.conn = conn
        
    def get_name(self):
        self.name = self.send(["register"])
        return self.name
    
    def get_stone(self):
        return self.stone

    def set_stone(self, color):
        self.stone = color
        command = ["receive-stones"]
        command.append(color)
        self.send(command)

    def make_move(self, boards):
        command = ["make-a-move"]
        command.append(boards)
        return self.send(command)

    def send(self, message):
        self.conn.send(str.encode(json.dumps(message)))
        resp = self.conn.recv(1024).decode("UTF-8")
        if not resp:
            return self.close()
        return resp


    def close(self):
        return "close"

    



class DefaultPlayer(AbstractPlayer):

    def make_move(self, boards: List):# -> str:
        """
        Determines the make-move strategy based on the parameter n
        Returns: 
            -"pass" if there are no valid moves
            -first valid point by column-row order
            -first valid point that leads to a capture of the opponent
            -first valid point of a sequence of moves that lead to a capture
        """
        if self.depth > 1:
            result = self.make_move_future(boards)
            if result:
                return result
        
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_stone())
        #If list is empty then there are no valid moves
        if not valid_moves: 
            return PASS_OUTPUT
        capture_point = self.make_move_capture(boards, valid_moves)
        #If no moves lead to an opponent capture - return first valid point
        if not capture_point:
            return valid_moves[0]
        return capture_point
    
    def make_move_capture(self, boards:List, valid_moves:List[str]):# -> Union[bool, str]:
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise 
        """
        boards = deepcopy(boards)
        for point in valid_moves: 
            if Board(boards[0]).check_future_liberties(point, self.get_stone()):
                return point
        return False
        
    def all_valid_moves(self, boards: List, stone: str):# -> List[str]:
        """
        Returns a list of valid moves for a given board history and stone
        """
        valid_moves, valid_capture_moves = [], []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
                if rulecheck(boards, stone, new_point):
                    valid_moves.append(new_point)
                    if self.find_next_capture_move(boards, new_point):
                        valid_capture_moves.append(new_point)
        return valid_moves, valid_capture_moves

    def find_next_capture_move(self, boards:List, point: str):# -> Union[bool, str]:
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise
        """
        boards = deepcopy(boards)
        if Board(boards[0]).check_future_liberties(point, self.get_stone()):
            return True
        return False

    def make_move_future(self, boards: List):

        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_stone())
        if len(boards) == 1 or len(boards) == 2:
            return valid_moves[0]

        if self.depth == 1 and valid_capture_moves:
            return valid_capture_moves[0]
        elif self.depth == 1 and valid_moves:
            return valid_moves[0]
        elif self.depth > 1:
            capture = self.make_move_recursive([], boards, self.depth) # or call make_move_points_of_interest here
            if capture:
                return capture
            elif valid_moves:
                return valid_moves[0]
            else:
                return PASS_OUTPUT
        else:
            return PASS_OUTPUT


    def make_move_recursive(self, list_of_moves: List, boards:List, n: int):# -> str:
        """
        Steps: 
            1.Finds and iterates through valid player moves
            2.For each valid player move 
            3.Find and iterate through valid opponent moves
            4.Make valid opponent move
            5.Call self recursive move on new update board state after player and opponent valid moves
        """
        boards = deepcopy(boards)
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_stone())
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
            new_board = place_stone(boards[0], self.get_stone(), move)
            valid_opponent_moves, valid_opponent_capture_moves = self.all_valid_moves([new_board, boards[0], boards[1]], opposite_stone)
            leads_to_capture = True
            for opponent_move in valid_opponent_moves:
                #if opponent_move in valid_opponent_capture_moves or \
                #        opponent_move in valid_capture_moves: <-- tried adding this, didn't work for some reason
                ## but I will try debugging
                    new_board2 = place_stone(new_board, opposite_stone, opponent_move)
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



class RemoteValidPlayer(AbstractPlayer):
    def make_move(self, boards: List):# -> str:
        """
        Determines the make-move strategy based on the parameter n
        Returns: 
            -"pass" if there are no valid moves
            -first valid point by column-row order
            -first valid point that leads to a capture of the opponent
            -first valid point of a sequence of moves that lead to a capture
        """

        choice = random.randint(0, 100)
        if not choice:
            #return self.make_invalid_move(boards)
            return "close"
        return self.make_valid_move(boards)


        """if self.depth > 1:
            result = self.make_move_future(boards)
            if result:
                return result
        
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_stone())
        #If list is empty then there are no valid moves
        if not valid_moves: 
            return PASS_OUTPUT
        capture_point = self.make_move_capture(boards, valid_moves)
        #If no moves lead to an opponent capture - return first valid point
        if not capture_point:
            return valid_moves[0]
        return capture_point"""


    def make_valid_move(self, boards:List):
        for row in range(BOARD_ROWS_MAX):
            for column in range(BOARD_COLUMNS_MAX):
                new_point = str(row + 1) + "-" + str(column + 1)
                if rulecheck(boards, self.get_stone(), new_point):
                    return new_point
        return "pass"
    
    def make_invalid_move(self, boards:List):
        return str(BOARD_COLUMNS_MAX + 1) + "-" + str(BOARD_COLUMNS_MAX + 1)
    
    def make_move_capture(self, boards:List, valid_moves:List[str]):# -> Union[bool, str]:
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise 
        """
        boards = deepcopy(boards)
        for point in valid_moves: 
            if Board(boards[0]).check_future_liberties(point, self.get_stone()):
                return point
        return False
        
    def all_valid_moves(self, boards: List, stone: str):# -> List[str]:
        """
        Returns a list of valid moves for a given board history and stone
        """
        valid_moves, valid_capture_moves = [], []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
                if rulecheck(boards, stone, new_point):
                    valid_moves.append(new_point)
                    if self.find_next_capture_move(boards, new_point):
                        valid_capture_moves.append(new_point)
        return valid_moves, valid_capture_moves

    def find_next_capture_move(self, boards:List, point: str):# -> Union[bool, str]:
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise
        """
        boards = deepcopy(boards)
        if Board(boards[0]).check_future_liberties(point, self.get_stone()):
            return True
        return False

    def make_move_future(self, boards: List):

        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_stone())
        if len(boards) == 1 or len(boards) == 2:
            return valid_moves[0]

        if self.depth == 1 and valid_capture_moves:
            return valid_capture_moves[0]
        elif self.depth == 1 and valid_moves:
            return valid_moves[0]
        elif self.depth > 1:
            capture = self.make_move_recursive([], boards, self.depth) # or call make_move_points_of_interest here
            if capture:
                return capture
            elif valid_moves:
                return valid_moves[0]
            else:
                return PASS_OUTPUT
        else:
            return PASS_OUTPUT


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
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_stone())
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
            new_board = place_stone(boards[0], self.get_stone(), move)
            valid_opponent_moves, valid_opponent_capture_moves = self.all_valid_moves([new_board, boards[0], boards[1]], opposite_stone)
            leads_to_capture = True
            for opponent_move in valid_opponent_moves:
                #if opponent_move in valid_opponent_capture_moves or \
                #        opponent_move in valid_capture_moves: <-- tried adding this, didn't work for some reason
                ## but I will try debugging
                    new_board2 = place_stone(new_board, opposite_stone, opponent_move)
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