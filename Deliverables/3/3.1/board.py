import dataclasses
import typing
import enum

from definitions import *
from dataclasses import field
from typing import List, Union

def check_maybestone(Stone: str, Operation:str = ""):
    if(Stone not in MAYBE_STONE):
        raise Exception("Invalid MaybeStone - cannot perform " + Operation + " operation")

def check_stone(Stone: str, Operation: str = ""):
    if(Stone not in STONE):
        raise Exception("Invalid Stone - cannot perform " + Operation + " operation")

@dataclasses
class BoardPoint:

    PointString: str
    x: int = field(init=False)
    y: int = field(init=False)

    def __post_init__(self):
        separatedString = self.PointString.split("-")
        self.x = separatedString[0]
        self.y = separatedString[1]
        if(not (self.x >= BOARD_COLUMNS_MIN and self.x <= BOARD_COLUMNS_MAX)):
            raise Exception("Point is out of bonds")
        elif(not (self.y >= BOARD_ROWS_MIN and self.y <= BOARD_COLUMNS_MAX)):
            raise Exception("Point is out of bounds")
    
@dataclasses
class Board: 

    board: List[List]

    def __post_init__(self):
        if(not len(self.board) == BOARD_ROWS_MAX): 
            raise Exception("Incorrect number of rows")
        for row in self.board: 
            if(not len(row) == BOARD_COLUMNS_MAX):
                raise Exception("Incorrect number of columns")
            for elem in row: 
                if elem not in MAYBE_STONE:
                    raise Exception("Invalid Point in Board")

    def occupied(self, Point: str) -> bool:
        point = BoardPoint(Point)
        return bool(self.board[point.y][point.x]) 

    def occupies(self, Point: str, Stone: str) -> bool: 
        point = BoardPoint(Point)
        check_stone(Stone, "occupies")
        if(self.board[point.y][point.x] == Stone):
            return True
        return False

    def reachable(self, Point: str, Stone: str) -> bool: 
        point = BoardPoint(Point)
        check_maybestone(Stone, "reachable")
        return self.find(point, Stone)

    def find(self, x: int, y: int, GoalStone: str) -> bool:
        currStone = self.board[y][x]
        if (currStone == GoalStone):
            return True
        elif (x + 1 <= BOARD_COLUMNS_MAX and self.board[y][x + 1] == currStone):
            return find(x + 1, y, GoalStone)
        elif (x - 1 >= BOARD_COLUMNS_MIN and self.board[y][x - 1] == currStone):
            return find(x - 1, y, GoalStone)
        elif (y + 1 <= BOARD_ROWS_MAX and self.board[y + 1][x] == currStone):
            return find(x, y + 1, GoalStone)
        elif (y - 1 >= BOARD_ROWS_MIN and self.board[y - 1][x] == currStone):
            return find(x, y - 1, GoalStone)
        else:
            return False

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
                return True
            if curr_x + 1 <= BOARD_COLUMNS_MAX:
                rightNeighbor = self.board[curr_y][curr_x + 1]
                if rightNeighbor == GoalStone:
                    return True
                if rightNeighbor == startStone:
                    stack.append((curr_x + 1, curr_y))
            if curr_x - 1 >= BOARD_COLUMNS_MIN:
                leftNeighbor = self.board[curr_y][curr_x - 1]
                if leftNeighbor == GoalStone:
                    return True
                if leftNeighbor == startStone:
                    stack.append((curr_x - 1, curr_y))
            if curr_y + 1 <= BOARD_ROWS_MAX:
                bottomNeighbor = self.board[curr_y + 1][curr_x]
                if bottomNeighbor == GoalStone:
                    return True
                if bottomNeighbor == startStone:
                    stack.append((curr_x, curr_y + 1))
            if curr_y - 1 >= BOARD_ROWS_MIN:
                topNeighbor = self.board[curr_y - 1][curr_x]
                if topNeighbor == GoalStone:
                    return True
                if topNeighbor == startStone:
                    stack.append((curr_x, curr_y - 1))
            visited.append((curr_x, curr_y))
        return False


    def place(self, Stone: str, Point: str) -> Union(List[List], str):
        point = BoardPoint(Point)
        check_stone(Stone, "place")
        if(self.board[point.y][point.x] in STONE):
            return "This seat is taken!"
        self.board[point.y][point.x] = Stone
        return self.board

    def remove(self, Stone: str, Point: str) -> Union(List[List], str):
        point = BoardPoint(Point)
        check_stone(Stone, "remove")
        existingStone = self.board[point.y][point.x]
        if(existingStone != Stone):
            return "I am just a Board! I cannot remove what is not there!"
        self.board[point.y][point.x] = ""
        return self.board

    def get_points(self, Stone: str) -> List:
        check_maybestone(Stone, "get-points")
        point_list = []
        for row in range(len(self.board)): 
            for column in range(len(self.board)): 
                if self.board[column][row] == Stone:
                    point_list.append(column,row)
        point_list.sort(key=lambda k : k[0],k[1])
        map(lambda k : str(k[0])+"-"+str(k[1]), point_list)
        return point_list


    