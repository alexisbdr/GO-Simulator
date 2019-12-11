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
import copy
#kill $(lsof -t -i:8080)

class AbstractPlayer(ABC):

    def __init__(self):
        self.name = ""
        self.stone = ""
        self.registered = False
        self.ended = False 

    def __eq__(self, other):
        if isinstance(other, AbstractPlayer):
            return self.name == other.name
        return False

    def __hash__(self):
        return id(self)

    def register(self):
        if self.registered:
            raise PlayerException("Player has already been registered")
        self.registered = True
        return self.name
        
    #some methods we will need
    def get_name(self):# -> str:
        if self.registered:
            return self.name
        raise PlayerException("Player has not been registered yet")
    
    def set_stone(self, stone: str):
        if not self.registered:
            raise PlayerException("Player has not been registered yet")
        if stone not in STONE:
            raise StoneException("Invalid Stone in Player")
        self.stone = stone
        self.ended = False

    def receive_stones(self, stone: str):
        self.set_stone(stone)
        return "RECEIVE"
    
    def get_stone(self):
        if self.stone:
            return self.stone
        else: 
            raise StoneException("Player color has not been set")
    
    def get_opponent_color(self):
        return "B" if self.get_stone() == "W" else "W"
    
    def end_game(self):
        if self.ended:
            raise PlayerException("Player has already been notified of game end")
        self.ended = True
        self.stone = ""
        return "OK"
    
    def is_connected(self):
        return False
    
    @abstractmethod
    def make_move(self, boards: List, n: int) -> str:
        pass


class ProxyPlayer(AbstractPlayer):
    
    def _init__(self):
        self.name = ""
        self.stone = ""
        
    def set_conn(self, conn):
        self.conn = conn
        self.client_connected = True
    
    def register(self):
        super().register()
        self.name = self.send(["register"])
        return self.name

    def receive_stones(self, color):
        super().set_stone(color)
        command = ["receive-stones"]
        command.append(color)
        message = json.dumps(command)
        self.conn.sendall(message.encode())
        return

    def make_move(self, boards):
        command = ["make-a-move"]
        command.append(boards)
        result = self.send(command)
        return result
    
    def end_game(self):
        command = ["end-game"]
        result = self.send(command)
        return result
    
    def is_connected(self):
        return self.client_connected

    def send(self, message):
        #print("sent message", message)
        try:
            message = json.dumps(message)
            self.conn.sendall(message.encode("UTF-8"))
            resp = self.conn.recv(4096).decode("UTF-8")
            #print("received message", resp)
            return resp
        except BrokenPipeError:
            print("remote player not connected")
            #self.client_connected = False
            return False


class DefaultPlayer(AbstractPlayer):
    def __init__(self):
        super().__init__()
        self.name = "Default Player"
        self.load_config()

    def load_config(self):
        config = readConfig(PLAYER_CONFIG_PATH)
        self.depth = config[0]

    def make_move(self, boards: List):# -> str:
        """
        Determines the make-move strategy based on the parameter n
        Returns: 
            -"pass" if there are no valid moves
            -first valid point by column-row order
            -first valid point that leads to a capture of the opponent
            -first valid point of a sequence of moves that lead to a capture
        """

        """choice = random.randint(0, 100)
        if not choice:
            return self.make_invalid_move(boards)"""

        return PASS_OUTPUT

        if self.depth > 1:
            result = self.make_move_future(boards)
            if result:
                return result
        
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, self.get_stone())
        if len(valid_moves) == 1:
            return PASS_OUTPUT
        #If list is empty then there are no valid moves
        if not valid_moves: 
            return PASS_OUTPUT
        capture_point = self.make_move_capture(boards, valid_moves)
        #If no moves lead to an opponent capture - return first valid point
        if not capture_point:
            return valid_moves[0]
        return capture_point

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


class RemoteTestingPlayer(AbstractPlayer):
    """
    Accepts a strategy and asks it to play
    """
    def __init__(self):
        super().__init__()
    
    def set_strategy(self, strategy):
        self.strategy = strategy
        self.name = strategy.__class__.__name__
        print(self.name)
    
    def make_move(self, boards: List):
        self.strategy.apply_strategy(boards, self.get_stone())
