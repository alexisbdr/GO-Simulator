import json
from typing import List, Union, Tuple


from board import Board
from definitions import *

def command_parser(command: List[str]) -> bool:
    #Handle Scoring
    if len(command) == 19: 
        return Board(command).count_score()
    else:
        #Handle pass command
        if command[1] == "pass":
            if command[0] not in STONE:
                #IS THIS FALSE OR EXCEPT
                raise Exception("Invalid Stone in pass command")
            else: 
                return True
        else: 
            return rulecheck(command)

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
    board = Board(board)
    #Check empty intersection
    if board.occupied(Point):
        return False
    board.place(Stone, Point)
    opposite_stone = "B" if Stone == "W" else "W"
    updated_board = board.remove_nonliberties(opposite_stone)
    suicide_board = board.remove_nonliberties(Stone)
    #Illegal Suicide
    if suicide_board != updated_board: 
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
    board1 = Board(board1)
    board2 = Board(board2)
    board1_b = board1.get_points("B")
    board2_b = board2.get_points("B")
    board1_w = board1.get_points("W")
    board2_w = board2.get_points("W")

    diff_b = len(board2_b) - len(board1_b)
    diff_w = len(board2_w) - len(board1_w)
    #Check for pass
    if board1_b == board2_b and board1_w == board2_w:
        return ("", "pass")
    #Check for invalid added stone at previously occupied position
    elif any(x in board1_b for x in board2_w) or any(x in board1_w for x in board2_b):
        return False
    #Check if both white and black decrease
    elif diff_b < 0 and diff_w < 0: 
        return False
    #Check for increase of both white and black pieces
    elif diff_b >= 1 and diff_w >= 1:
        return False
    #Check for increase of either black and white by more than 1
    elif diff_b > 1 or diff_w > 1: 
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
        return False
    #Covers non-order turns after a pass
    elif turn2[0] == "pass" and turn1[0] != turn3[0]: 
        return False
    return True

def checkKo(boards: List[Board]) -> bool: 
    """
    Input: 
        List of boards
    Output: 
        False if violates Ko rule
        True if valid
    """
    if boards[0] == boards[2]:
        return False
    elif boards[1] == boards[3]:
        return False
    
    return True

def rulecheck(command: List[str]):
    #Handle
    boards = command[1][1]
    #Check Empty Board 
    if len(boards) == 1:
        return Board(boards).Empty() and command[0] == "B"
    elif len(boards) == 2:
        if not Board(boards[1]).Empty():
            return False
        turn1 = findAddedPoint(boards[1], boards[0])
        if not turn1 or turn1[0] != "B":
            return False

        move2 = makemove(boards[0], command[0], command[1][0])
        if not move2:
            return False
        
        return True
        
    elif len(boards) == 3: 
        #Check Valid turns
        turn1 = findAddedPoint(boards[2], boards[1])
        if not turn1: 
            return False
        move1 = makemove(boards[2], turn1[0], turn1[1])
        if not move1 or move1 != boards[1]:
            return False

        turn2 = findAddedPoint(boards[1], boards[0])
        if not turn2: 
            return False
        move2 = makemove(boards[1], turn2[0], turn2[1])
        if not move2 or move2 != boards[0]:
            return False

        move3 = makemove(boards[0], command[0], command[1][0])
        if not move3:
            return False
        turn3 = (command[0], command[1][0])
        boards = list(move3, boards[0], boards[1], boards[2])

        return checkTurn(turn1, turn2, turn3) or checkKo(boards)


    
