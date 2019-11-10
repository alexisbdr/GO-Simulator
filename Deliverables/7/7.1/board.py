import typing
import enum
import json
from copy import deepcopy
from itertools import product
from exceptions import MaybestoneException, StoneException, BoardPointException, BoardException

from definitions import *
from typing import Any, List, Union

def check_maybestone(Stone: str, Operation:str = ""):
    if(Stone not in MAYBE_STONE):
        raise MaybestoneException("Invalid MaybeStone - cannot perform " + Operation + " operation")

def check_stone(Stone: str, Operation: str = ""):
    if(Stone not in STONE):
        raise StoneException("Invalid Stone - cannot perform " + Operation + " operation")

def get_all_string_points() -> List[str]:
    return [
        str(row+1)+"-"+str(column+1) for row, column in \
            product(range(BOARD_COLUMNS_MAX), range(BOARD_ROWS_MAX))
    ]

class BoardPoint:

    def __init__(self, Point: str):
        self.PointString = Point
        try:
            separatedString = self.PointString.split("-")
            self.x = int(separatedString[0])
            self.y = int(separatedString[1])
            self.x_ind = self.x - 1
            self.y_ind = self.y - 1
        except: 
            raise BoardPointException("Point is not in the right format")
        if(not (self.x >= BOARD_COLUMNS_MIN and self.x <= BOARD_COLUMNS_MAX)):
            raise BoardPointException("Point is out of bonds")
        elif(not (self.y >= BOARD_ROWS_MIN and self.y <= BOARD_COLUMNS_MAX)):
            raise BoardPointException("Point is out of bounds")

class Board: 

    def __init__(self, Board: List[List]):
        self.board = deepcopy(Board)
        
        #Performing Board checks
        if(not len(self.board) == BOARD_ROWS_MAX): 
            raise BoardException("Incorrect number of rows")
        for row in self.board: 
            if(not len(row) == BOARD_COLUMNS_MAX):
                raise BoardException("Incorrect number of columns")
            for elem in row: 
                if elem not in MAYBE_STONE:
                    raise BoardException("Invalid Point in Board")

    def Get(self, Point: str) -> str:
        point = BoardPoint(Point)
        return self.board[point.y - 1][point.x - 1]
    
    def Set(self, Point: str, Stone: str):
        point = BoardPoint(Point)
        self.board[point.y - 1][point.x - 1] = Stone
    
    def Empty(self) -> bool:
        for row in range(len(self.board)):
            for column in range(len(self.board)):
                if self.board[column][row] in STONE:
                    return False
        return True
    
    def occupied(self, Point: str) -> bool:
        if self.Get(Point) in STONE:
            return TRUE_OUTPUT
        else: return FALSE_OUTPUT

    def occupies(self, Stone: str, Point: str) -> bool:
        check_stone(Stone, "occupies")
        if(self.Get(Point) == Stone):
            return TRUE_OUTPUT
        else: return FALSE_OUTPUT

    def reachable(self, Point: str, Stone: str) -> bool:
        point = BoardPoint(Point)
        check_maybestone(Stone, "reachable")
        return self.find2(point.x_ind, point.y_ind, Stone)
    
    def find2(self, x: int, y:int, GoalStone: str) -> bool:
        startStone = self.board[y][x]
        visited = []
        stack = []
        stack.append((x, y))
        while len(stack) > 0:
            curr_x, curr_y = stack.pop()
            if (curr_x, curr_y) in visited:
                continue
            if self.board[curr_y][curr_x] == GoalStone:
                return TRUE_OUTPUT
            if curr_x + 1 < BOARD_COLUMNS_MAX:
                rightNeighbor = self.board[curr_y][curr_x + 1]
                if rightNeighbor == GoalStone:
                    return TRUE_OUTPUT
                if rightNeighbor == startStone:
                    stack.append((curr_x + 1, curr_y))
            if curr_x - 1 > -BOARD_COLUMNS_MIN:
                leftNeighbor = self.board[curr_y][curr_x - 1]
                if leftNeighbor == GoalStone:
                    return TRUE_OUTPUT
                if leftNeighbor == startStone:
                    stack.append((curr_x - 1, curr_y))
            if curr_y + 1 < BOARD_ROWS_MAX:
                bottomNeighbor = self.board[curr_y + 1][curr_x]
                if bottomNeighbor == GoalStone:
                    return TRUE_OUTPUT
                if bottomNeighbor == startStone:
                    stack.append((curr_x, curr_y + 1))
            if curr_y - 1 > -BOARD_ROWS_MIN:
                topNeighbor = self.board[curr_y - 1][curr_x]
                if topNeighbor == GoalStone:
                    return TRUE_OUTPUT
                if topNeighbor == startStone:
                    stack.append((curr_x, curr_y - 1))
            visited.append((curr_x, curr_y))
        return FALSE_OUTPUT


    def place(self, Stone: str, Point: str) -> Union[List[List], str]:
        check_stone(Stone, "place")
        if self.occupied(Point):
            return PLACE_ERROR_MESSAGE
        else: 
            self.Set(Point, Stone)
            return self.board

    def remove(self, Stone: str, Point: str) -> Union[List[List], str]:
        check_stone(Stone, "remove")
        if not self.occupies(Stone, Point) :
            return REMOVE_ERROR_MESSAGE
        else: 
            self.Set(Point, EMPTY_STONE)
            return self.board
    
    def remove_nonliberties(self, Stone: str):
        points_to_check = self.get_points(Stone)
        points_to_remove = []
        for point in points_to_check: 
            if not self.reachable(point, EMPTY_STONE):
                points_to_remove.append(point)
        for point in points_to_remove:
            self.board = self.remove(Stone, point)
        return self.board
    
    def check_future_liberties(self, Point: str, Stone: str):
        self.place(Stone, Point)
        opposite_stone = "B" if Stone == "W" else "W"
        old_board = deepcopy(self.board)
        if old_board != self.remove_nonliberties(opposite_stone):
            return True
        return False

    def get_points(self, Stone: str) -> List:
        check_maybestone(Stone, "get-points")
        point_list = []
        for row in range(len(self.board)): 
            for column in range(len(self.board)): 
                if self.board[column][row] == Stone:
                    point_list.append((row,column))
        point_list = list(map(lambda k : str(k[0]+1)+"-"+str(k[1]+1), point_list))
        point_list.sort()
        return point_list
    
    def count_score(self) -> dict:
        score = {}
        score["B"] = len(self.get_points("B"))
        score["W"] = len(self.get_points("W"))
        if score["B"] == 0 and score["W"] == 0: 
            return score
        empty_stones = self.get_points(" ")
        for point in empty_stones: 
            reach_b = self.reachable(point, "B")
            reach_w = self.reachable(point, "W")
            if reach_b and reach_w:
                continue
            elif reach_b and not reach_w:
                score["B"] += 1
            elif reach_w and not reach_b: 
                score["W"] += 1
            else: 
                continue
        return score
    


    



    