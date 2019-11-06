import typing
import enum
import json
from copy import deepcopy
from itertools import product

from definitions import *
from typing import Any, List, Union

def check_maybestone(Stone: str, Operation:str = ""):
    if(Stone not in MAYBE_STONE):
        raise Exception("Invalid MaybeStone - cannot perform " + Operation + " operation")

def check_stone(Stone: str, Operation: str = ""):
    if(Stone not in STONE):
        raise Exception("Invalid Stone - cannot perform " + Operation + " operation")

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
            raise Exception("Point is not in the right format")
        if(not (self.x >= BOARD_COLUMNS_MIN and self.x <= BOARD_COLUMNS_MAX)):
            raise Exception("Point is out of bonds")
        elif(not (self.y >= BOARD_ROWS_MIN and self.y <= BOARD_COLUMNS_MAX)):
            raise Exception("Point is out of bounds")
    
    def to_string(self, x: int, y: int) -> str:
        return str(x) + "-" + str(y)

    def to_coord(self, Point: str):
        return Point.split("-")[0], Point.split("-")[1]

    def right_neighbor(self) -> str:
        if self.x + 1 <= BOARD_COLUMNS_MAX:
            return self.to_string(self.x + 1, self.y)
        return None

    def left_neighbor(self) -> str: 
        if self.x - 1 >= BOARD_COLUMNS_MIN: 
            return self.to_string(self.x - 1, self.y)
        return None

    def up_neighbor(self) -> str: 
        if self.y - 1 >= BOARD_ROWS_MIN:
            return self.to_string(self.x, self.y - 1)
        return None

    def down_neighbor(self) -> str: 
        if self.y + 1 <= BOARD_ROWS_MAX: 
            return self.to_string(self.x, self.y + 1)
        return None

    def neighbors(self) -> List[str]:
        return [
            self.right_neighbor(), 
            self.left_neighbor(), 
            self.up_neighbor(), 
            self.down_neighbor()
            ]

class Board: 

    def __init__(self, Board: List[List] = None):
        self.board = deepcopy(Board)
        if Board is None: 
            self.EmptyBoard()        
        #Performing Board checks
        if(not len(self.board) == BOARD_ROWS_MAX): 
            raise Exception("Incorrect number of rows")
        for row in self.board: 
            if(not len(row) == BOARD_COLUMNS_MAX):
                raise Exception("Incorrect number of columns")
            for elem in row: 
                if elem not in MAYBE_STONE:
                    raise Exception("Invalid Point in Board")

    def GetStone(self, Point: str) -> str:
        point = BoardPoint(Point)
        return self.board[point.y - 1][point.x - 1]
    
    def GetBoard(self) -> List[List]:
        return self.board
    
    def Set(self, Point: str, Stone: str):
        point = BoardPoint(Point)
        self.board[point.y - 1][point.x - 1] = Stone
    
    def isEmpty(self) -> bool:
        for row in range(len(self.board)):
            for column in range(len(self.board)):
                if self.board[column][row] in STONE:
                    return False
        return True
    
    def EmptyBoard(self) -> List[List[str]]:
        board = []
        for row in range(BOARD_ROWS_MAX):
            row = []
            for column in range(BOARD_COLUMNS_MAX):
                row.append(EMPTY_STONE)
            board.append(row)
        self.board = board
    
    def occupied(self, Point: str) -> bool:
        if self.GetStone(Point) in STONE:
            return TRUE_OUTPUT
        else: return FALSE_OUTPUT

    def occupies(self, Stone: str, Point: str) -> bool:
        check_stone(Stone, "occupies")
        if(self.GetStone(Point) == Stone):
            return TRUE_OUTPUT
        else: return FALSE_OUTPUT

    def reachable(self, Point: str, Stone: str) -> bool:
        point = BoardPoint(Point)
        check_maybestone(Stone, "reachable")
        return self.find2(Point, Stone)

    def find2(self, Point: str, GoalStone: str) -> bool:
        startStone = self.GetStone(Point)
        visited = []
        stack = []
        stack.append((Point))
        while len(stack) > 0:
            curr_point = stack.pop()
            if curr_point in visited:
                continue
            if self.GetStone(curr_point) == GoalStone:
                return TRUE_OUTPUT
            for point in BoardPoint(curr_point).neighbors():
                if point and self.GetStone(point) == GoalStone:
                    return TRUE_OUTPUT
                if point and self.GetStone(point) == startStone:
                    stack.append(point)
            visited.append(curr_point)
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
    


    



    