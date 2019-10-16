import typing
import enum
import json

from definitions import *
from typing import Any, List, Union


def check_maybestone(Stone: str, Operation: str = ""):
    if (Stone not in MAYBE_STONE):
        raise Exception("Invalid MaybeStone - cannot perform " + Operation + " operation")


def check_stone(Stone: str, Operation: str = ""):
    if (Stone not in STONE):
        raise Exception("Invalid Stone - cannot perform " + Operation + " operation")


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
        if (not (self.x >= BOARD_COLUMNS_MIN and self.x <= BOARD_COLUMNS_MAX)):
            raise Exception("Point is out of bonds")
        elif (not (self.y >= BOARD_ROWS_MIN and self.y <= BOARD_COLUMNS_MAX)):
            raise Exception("Point is out of bounds")


class Board:

    def __init__(self, Board: List[List], Statement: List):
        self.board = Board
        self.statement = Statement
        # Performing Board checks
        if (not len(self.board) == BOARD_ROWS_MAX):
            raise Exception("Incorrect number of rows")
        for row in self.board:
            if (not len(row) == BOARD_COLUMNS_MAX):
                raise Exception("Incorrect number of columns")
            for elem in row:
                if elem not in MAYBE_STONE:
                    raise Exception("Invalid Point in Board")

        # Perform Statement Checks
        query_command = self.statement[0]
        if not (query_command in COMMANDS and \
                len(self.statement) == COMMANDS[query_command]):
            raise Exception("Invalid Command **WRONG NUMBER OF INPUTS** - Please try again")
        if query_command == "occupied?":
            self.occupied(self.statement[1])
        elif query_command == "occupies?":
            self.occupies(self.statement[1], self.statement[2])
        elif query_command == "reachable?":
            self.reachable(self.statement[1], self.statement[2])
        elif query_command == "place":
            self.place(self.statement[1], self.statement[2])
        elif query_command == "remove":
            self.remove(self.statement[1], self.statement[2])
        elif query_command == "get-points":
            self.get_points(self.statement[1])

    def occupied(self, Point: str) -> bool:
        point = BoardPoint(Point)
        if self.board[point.y_ind][point.x_ind] in STONE:
            self.result = TRUE_OUTPUT
        else:
            self.result = FALSE_OUTPUT

    def occupies(self, Stone: str, Point: str) -> bool:
        point = BoardPoint(Point)
        check_stone(Stone, "occupies")
        if (self.board[point.y_ind][point.x_ind] == Stone):
            self.result = TRUE_OUTPUT
        else:
            self.result = FALSE_OUTPUT

    def reachable(self, Point: str, Stone: str) -> bool:
        point = BoardPoint(Point)
        check_maybestone(Stone, "reachable")
        self.result = self.find2(point.x_ind, point.y_ind, Stone)

    def find2(self, x: int, y: int, GoalStone: str) -> bool:
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
        point = BoardPoint(Point)
        check_stone(Stone, "place")
        if (self.board[point.y_ind][point.x_ind] in STONE):
            self.result = PLACE_ERROR_MESSAGE
        else:
            self.board[point.y_ind][point.x_ind] = Stone
            self.result = self.board

    def remove(self, Stone: str, Point: str) -> Union[List[List], str]:
        point = BoardPoint(Point)
        check_stone(Stone, "remove")
        existingStone = self.board[point.y_ind][point.x_ind]
        if (existingStone != Stone):
            self.result = REMOVE_ERROR_MESSAGE
        else:
            self.board[point.y_ind][point.x_ind] = EMPTY_STONE
            self.result = self.board

    def get_points(self, Stone: str) -> List:
        check_maybestone(Stone, "get-points")
        point_list = []
        for row in range(len(self.board)):
            for column in range(len(self.board)):
                if self.board[column][row] == Stone:
                    point_list.append((row, column))
        point_list = list(map(lambda k: str(k[0] + 1) + "-" + str(k[1] + 1), point_list))
        point_list.sort()
        self.result = point_list

    def __repr__(self):
        return json.dumps(self.result)



    