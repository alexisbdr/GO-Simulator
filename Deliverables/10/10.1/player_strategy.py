from typing import List
import random
from abc import ABC, abstractmethod
from copy import deepcopy
import numpy as np
from collections import defaultdict

from mcts import state, mc_search, mc_node

from rulechecker import rulecheck, place_stone
from board import get_all_string_points, Board
from definitions import PASS_OUTPUT, BOARD_COLUMNS_MAX, BOARD_COLUMNS_MIN

def create_strategy():
    choice = random.randint(0,9)
    if choice == 0: 
        return ClassicStrategy()
    elif choice == 1: 
        return ReversedStrategy()
    elif choice == 2:
        return RandomStrategy()
    elif choice == 3: 
        return EndGameStrategy()
    elif choice == 4:
        return TuringValidPlayer()
    #elif choice == 5:
    #    return TuringAdvancedValidPlayer()
    elif choice == 6:
        return OccupiedStrategy()
    elif choice == 7: 
        return SuicideStrategy()
    elif choice == 8: 
        return OutOfBoundsStrategy()
    elif choice == 9: 
        return CloseConnectionStrategy()
    elif choice == 10:
        return CrazyStringStrategy() 
    return ClassicStrategy()
        
class PlayerStrategy(ABC):
    """
    Abstract Base Class for the player strategy
    """

    @abstractmethod
    def apply_strategy(self, boards: List, stone: str):
        pass

class SimplePlayerStrategy(PlayerStrategy):
    """
    Simple Valid
    """
    
    def all_valid_moves(self, boards: List, stone: str):
        """
        Returns a list of valid moves for a given board history and stone
        """
        valid_moves = []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
            if rulecheck(boards, stone, new_point):
                valid_moves.append(new_point)
        if len(valid_moves) <= 1:
            return ["pass"]
        return valid_moves
    
class ClassicStrategy(SimplePlayerStrategy):
    """
    Makes first valid move TopLeft
    """
 
    def apply_strategy(self, boards:List, stone: str):
        valid_moves = self.all_valid_moves(boards, stone)
        return valid_moves[0]

class ReversedStrategy(SimplePlayerStrategy):
    """
    Makes first valid move BottomRight
    """
    
    def apply_strategy(self, boards:List, stone: str):
        valid_moves = self.all_valid_moves(boards, stone)
        return valid_moves[-1]

class RandomStrategy(SimplePlayerStrategy):
    """
    Makes random valid moves anywhere it fucking wants
    """

    def apply_strategy(self, boards: List, stone: str):
        valid_moves = self.all_valid_moves(boards, stone)
        if valid_moves:
            choice = random.randint(0, len(valid_moves) - 1)
            return valid_moves[choice]
        return "pass"

class EndGameStrategy(SimplePlayerStrategy):

    def __init__(self):
        self.pass_flag = False
        self.pass_turn = random.randint(0,100)
        self.turn = 0
    
    def apply_strategy(self, boards: List, stone: str):
        if self.turn == self.pass_turn or self.pass_flag:
            self.pass_flag = True
            return "pass"
        valid_moves = self.all_valid_moves(boards, stone)
        return valid_moves[0]

class CapturePlayerStrategy(PlayerStrategy):
    """
    Randomly chooses one of the advnaced player strategies composed of: 
        Turing (n=1), TuringAdvanced(n=2)
    """
    
    def make_move_capture(self, boards:List, valid_moves:List[str], stone):
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise 
        """
        boards = deepcopy(boards)
        for point in valid_moves: 
            if Board(boards[0]).check_future_liberties(point, stone):
                return point
        return False
    
    def find_next_capture_move(self, boards:List, point: str, stone: str):
        """
        Returns first valid point that leads to a capture of the opponent's pieces
        False otherwise
        """
        boards = deepcopy(boards)
        if Board(boards[0]).check_future_liberties(point, stone):
            return True
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
                    if self.find_next_capture_move(boards, new_point, stone):
                        valid_capture_moves.append(new_point)
        return valid_moves, valid_capture_moves

    def get_opponent_color(self, stone):
        return "B" if stone == "W" else "W"
    
class TuringValidPlayer(CapturePlayerStrategy):
    """
    The n=1 strategy from  assignment 4
    """
    
    def apply_strategy(self, boards: List, stone):# -> str:
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, stone)
        if len(valid_moves) == 1:
            return PASS_OUTPUT
        #If list is empty then there are no valid moves
        if not valid_moves: 
            return PASS_OUTPUT
        capture_point = self.make_move_capture(boards, valid_moves, stone)
        #If no moves lead to an opponent capture - return first valid point
        if not capture_point:
            choice = random.randint(0,len(valid_moves) - 1)
            return valid_moves[choice]
        return capture_point
    
class TuringAdvancedValidPlayer(CapturePlayerStrategy):

    def __init__(self):
        self.depth = 2

    def apply_strategy(self, boards: List, stone):
        valid_moves, valid_capture_moves = self.all_valid_moves(boards, stone)
        if len(boards) == 1 or len(boards) == 2:
            return valid_moves[0]

        if self.depth == 1 and valid_capture_moves:
            return valid_capture_moves[0]
        elif self.depth == 1 and valid_moves:
            return valid_moves[0]
        elif self.depth > 1:
            capture = self.make_move_recursive([], boards, stone) # or call make_move_points_of_interest here
            if capture:
                return capture
            elif valid_moves:
                return valid_moves[0]
            else:
                return PASS_OUTPUT
        else:
            return PASS_OUTPUT


    def make_move_recursive(self, list_of_moves: List, boards:List, stone) -> str:
        """
        Steps: 
            1.Finds and iterates through valid player moves
            2.For each valid player move 
            3.Find and iterate through valid opponent moves
            4.Make valid opponent move
            5.Call self recursive move on new update board state after player and opponent valid moves
        """
        boards = deepcopy(boards)
        valid_moves, valid_capture_moves = self.all_valid_moves(boards,stone) 
        opposite_stone = self.get_opponent_color(stone)
        if self.depth == 1: # if n == 1, we need to make a capture right away
            if self.make_move_capture(boards, valid_moves, stone):
                choice = random.randint(0, len(list_of_moves) - 1)
                return list_of_moves[choice]
            else:
                return None
        for move in valid_moves:
            list_of_moves.append(move)
            if self.make_move_capture(boards, [move], stone):
                choice = random.randint(0,len(list_of_moves) - 1)
                return list_of_moves[choice]
            new_board = place_stone(boards[0], stone, move)
            valid_opponent_moves, valid_opponent_capture_moves = self.all_valid_moves([new_board, boards[0], boards[1]], opposite_stone)
            leads_to_capture = True
            for opponent_move in valid_opponent_moves:
                #if opponent_move in valid_opponent_capture_moves or \
                #        opponent_move in valid_capture_moves: <-- tried adding this, didn't work for some reason
                ## but I will try debugging
                    new_board2 = place_stone(new_board, opposite_stone, opponent_move)
                    self.depth -= 1
                    result = self.make_move_recursive(list_of_moves, [new_board2, new_board, boards[0]], stone)
                    if result is None:
                        leads_to_capture = False
                        break
                    else:
                        continue
            if leads_to_capture:
                choice = random.randint(0, len(list_of_moves)- 1)
                return list_of_moves[choice]
            list_of_moves.pop()
        return None

class IllegalPlayerStrategy(PlayerStrategy):

    def make_valid_move(self, boards, stone):    
        valid_moves = self.all_valid_moves(boards, stone)
        #print(valid_moves)
        if valid_moves:
            choice_index = random.randint(0, len(valid_moves)-1)
            return valid_moves[choice_index]
        return "pass"

    def all_valid_moves(self, boards: List, stone: str):# -> List[str]:
        """
        Returns a list of valid moves for a given board history and stone
        """
        valid_moves = []
        all_string_points = get_all_string_points()
        for new_point in all_string_points: 
                if rulecheck(boards, stone, new_point):
                    valid_moves.append(new_point)
                    
        return valid_moves
    
    def get_opponent_color(self, stone):
        return "B" if stone == "W" else "W"

class OccupiedStrategy(IllegalPlayerStrategy):
    
    def __init__(self):
        self.invalid_turn = random.randint(0,100)
        self.turn = 0
    
    def apply_strategy(self, boards: List, stone):
        
        if self.turn == self.invalid_turn:
            return self.get_occupied_move(boards, stone)
        else:
            self.turn+=1 
            return self.make_valid_move(boards,stone)

    def get_occupied_move(self, boards, stone):
        board = Board(boards[0])
        opposite_points = board.get_points(self.get_opponent_color(stone))
        choice_index = random.randint(0, len(opposite_points))
        return opposite_points[choice_index]

class SuicideStrategy(IllegalPlayerStrategy):

    def __init__(self):
        self.invalid_turn = random.randint(0,100)
        self.turn = 0

    def apply_strategy(self, boards: List, stone):
        
        if self.turn == self.invalid_turn:
            return self.get_suicide_move(boards, stone)
        else:
            self.turn+=1 
            return self.make_valid_move(boards, stone)
        
    def get_suicide_move(self, boards, stone):
        board = Board(boards[0])
        empty_points = board.get_points(" ")
        suicide_points = []
        for point in empty_points:
            board_copy = deepcopy(board)
            board_copy.place(point, stone)
            result = board_copy.reachable(point, " ")
            if not result:
                suicide_points.append(point)
        
        if suicide_points:
            choice_index = random.randint(0, len(suicide_points))
            return suicide_points[choice_index]

        return False

class OutOfBoundsStrategy(IllegalPlayerStrategy):

    def __init__(self):
        self.invalid_turn = random.randint(0,100)
        self.turn = 0

    def apply_strategy(self, boards: List, stone):
        if self.turn == self.invalid_turn:
            return self.get_outofbounds_move()
        else:
            self.turn+=1 
            return self.make_valid_move(boards, stone)
      
    def get_outofbounds_move(self):
        return str(BOARD_COLUMNS_MAX + 1) + "-" + str(BOARD_COLUMNS_MAX + 1)

class CloseConnectionStrategy(IllegalPlayerStrategy):
    
    def __init__(self):
        self.invalid_turn = random.randint(0,100)
        self.turn = 0

    def apply_strategy(self, boards: List, stone):
        if self.turn == self.invalid_turn:
            return "close"
        else:
            self.turn+=1 
            return self.make_valid_move(boards, stone)

class CrazyStringStrategy(IllegalPlayerStrategy):

    def __init__(self):
        self.random_string = ''.join([random.choice(string.ascii_letters + \
            string.digits) for n in range(50)])
        self.invalid_turn = random.randint(0,INVALID_TURN)
        self.turn = 0

    def apply_strategy(self, boards: List, stone):
        if self.turn == self.invalid_turn:
            print("CrazyString strategy doing illegal move at turn: {}".format(self.turn))
            return self.random_string
        else:
            self.turn+=1 
            return self.make_valid_move(boards, stone)

class MonteCarloStrategy(PlayerStrategy):

    def apply_strategy(self, boards: List, stone):
        print("applying MC Strat")
        _state = state.GoGameState(boards[0], stone)
        root = mc_node.TwoPlayersGameMonteCarloTreeSearchNode(
                state=_state,
                parent=None)
        mcts = MonteCarloTreeSearch(root)
        assert mcts.best_action(3) 

