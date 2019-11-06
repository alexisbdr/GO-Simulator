import json
from typing import List, Union, Tuple
from copy import deepcopy


from board import Board
from definitions import *


def makemove(board: Board, Stone: str, Point: str) -> Board:
    """
    Inputs
        board: the board that represents the initial state on which we will apply the move
        Point: the point "X-Y" 
        Stone: the stone type
    What it does: 
        Applies the move on the board and returns the board
        Follows the following steps:
            1.Place stone on empty intersection
            2.Remove opponent stones that have no liberties
            3.Check for illegal suicide
    Outputs:
        the new Board if the move is valid
        False if the move is invalid
    """
    board = deepcopy(board)
    #Check for pass
    if Point == PASS_OUTPUT:
        return board.GetBoard()
    #Check empty intersection
    if board.occupied(Point):
        return False

    board.place(Stone, Point)

    opposite_stone = "B" if Stone == "W" else "W"
    updated_board = board.remove_nonliberties(opposite_stone)
    updated_board = Board(updated_board)
    suicide_board = deepcopy(updated_board)
    suicide_board = suicide_board.remove_nonliberties(Stone)
    #Illegal Suicide
    if suicide_board != updated_board.GetBoard():
        return False
    return updated_board

def findAddedPoint(board1: Board, board2: Board) -> Union[Tuple[str, str], bool]:
    """
    Inputs
        board1: the board that represents the initial state
        board2: the board that represents the state of board1 after a move have been made
    What it does: 
        Checks validity of the move and finds the valid stone that was added to the board
    Outputs:
        a (Point, Stone) tuple if the move was valid
        False if the move is invalid
        True if it was a pass
    """
    board1_ = deepcopy(board1)
    board2_ = deepcopy(board2)
    board1_b = board1_.get_points("B")
    board2_b = board2_.get_points("B")
    board1_w = board1_.get_points("W")
    board2_w = board2_.get_points("W")

    diff_b = len(board2_b) - len(board1_b)
    diff_w = len(board2_w) - len(board1_w)
    #Check for pass
    if board1_b == board2_b and board1_w == board2_w:
        return (EMPTY_STONE, PASS_OUTPUT)
    #Check for invalid added stone at previously occupied position
    elif any(x in board1_b for x in board2_w) or any(x in board1_w for x in board2_b):
        #print(count, "prev position")
        return False
    #Check if both white and black decrease
    elif diff_b < 0 and diff_w < 0: 
        #print(count, "decrease")
        return False
    #Check for increase of both white and black pieces
    elif diff_b >= 1 and diff_w >= 1:
        #print(count, "both white and black increase")
        return False
    #Check for increase of either black and white by more than 1
    elif diff_b > 1 or diff_w > 1:
        #print(count, "increase by more than 1")
        return False
    else: 
        if diff_b == 1: 
            added = set(board2_b) - set(board1_b)
            return ("B", list(added)[0])
        elif diff_w == 1: 
            added = set(board2_w) - set(board1_w)
            return ("W", list(added)[0])

def checkTurn(turn1: Tuple[str, str], turn2: Tuple[str, str], turn3: Tuple[str, str]):
    """
    Input: 
        List of turns that are either "B" "W" or "pass"
    """
    #Covers sequential turns
    if turn1[0] == turn2[0] or turn2[0] == turn3[0]:
        #print(count, "Sequential turns invalid")
        return False
    #Covers non-order turns after a pass
    elif turn2[0] == PASS_OUTPUT and turn1[0] != turn3[0]: 
        #print(count, "Invalid order after a pass")
        return False
    return True

def checkKo(board1: Board, board2: Board, board3: Board, board4: Board) -> bool: 
    """
    Input: 
        List of boards
    Output: 
        False if violates Ko rule
        True if valid
    """
    if board1.GetBoard() == board3.GetBoard():
        #print(count, "Ko - 0-2")
        return False
    if board2.GetBoard() == board4.GetBoard():
        #print(count, "Ko - 1-3")
        return False
    
    return True

def rulecheck_one(boards: List[Board], stone: str, position: str) -> bool:
  
   #Make a copy because the order of boards gets messed up --> for checkKo
    _boards = deepcopy(boards)
    #Check isEmpty Board 
    return _boards[0].isEmpty() and stone == "B"

def rulecheck_two(boards: List[Board], stone: str, position: str) -> bool:
    
    _boards = deepcopy(boards)
    if not _boards[1].isEmpty():
            return False
    turn1 = findAddedPoint(_boards[1], _boards[0])
    if not turn1 or turn1[0] == "W" or stone == "B":
        return False

    move2 = makemove(_boards[0], stone, position)
    if not move2:
        return False
    
    return True

def rulecheck_three(boards: List[Board], stone: str, position: str) -> bool:

    _boards = deepcopy(boards)
    #Check Valid turns
    turn1 = findAddedPoint(_boards[2], _boards[1])
    if not turn1: 
        return False
    move1 = makemove(_boards[2], turn1[0], turn1[1])
    if not move1 or move1 != _boards[1].GetBoard():
        #print(count, "invalid move1")
        return False

    turn2 = findAddedPoint(_boards[1], _boards[0])
    if not turn2: 
        return False
    move2 = makemove(_boards[1], turn2[0], turn2[1])
    if not move2 or move2 != boards[0].GetBoard():
        #print(count, "invalid move2")
        return False

    move3 = makemove(_boards[0], stone, position)
    if not move3:
        return False
    turn3 = (stone, position)
    
    if _boards[2].isEmpty() and _boards[1].isEmpty() and turn2[0] != "W":
        return False
    return checkTurn(turn1, turn2, turn3) and checkKo(move3, _boards[0], _boards[1], _boards[2])

    
