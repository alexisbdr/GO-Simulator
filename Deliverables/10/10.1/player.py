import json
import typing
from typing import List, Union
from copy import deepcopy
from board import Board,get_all_string_points,BoardPoint
from rulechecker import *
from definitions import *
from utilities import readConfig
from exceptions import StoneException, PlayerStateViolation, PlayerTypeError, BoardPointException
from player_strategy import PlayerStrategy
from abc import ABC, abstractmethod
import random
import copy
from socket import socket
#from graphics import *
import rulechecker
#kill $(lsof -t -i:8080)

class AbstractPlayer(ABC):

    def __init__(self):
        self.name = ""
        self.stone = ""

    def register(self):
        return self.name
        
    #some methods we will need
    def get_name(self):# -> str:
        return self.name

    def receive_stones(self, stone: str):
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
    
    def end_game(self):
        self.stone = ""
        return END_GAME_MESSAGE
    
    def is_connected(self):
        return False
    
    @abstractmethod
    def make_move(self, boards: List) -> str:
        pass

    def __eq__(self, other):
        if isinstance(other, AbstractPlayer):
            return self.get_name() == other.get_name()
        return False

    def __hash__(self):
        return id(self)

class ProxyStateContractPlayer(AbstractPlayer):

    def __init__(self, player):
        self.player = player
        self.registered = False
        self.received = False
        self.ended = False
        self.has_strategy = False
        self.client_connected = False

    def register(self):
        if self.registered:
            raise PlayerStateViolation("Player has already been registered")
        self.registered = True
        return self.player.register()
        
    def get_name(self):
        if self.registered:
            return self.player.get_name()
        raise PlayerStateViolation("Player has not been registered yet")
    
    def receive_stones(self, stone: str):
        if not self.registered: 
            raise PlayerStateViolation("Player has not been registered yet")
        if self.received: 
            raise PlayerStateViolation("Player has received stones")
        self.received = True
        self.ended = False
        self.player.receive_stones(stone)
    
    def get_stone(self):
        if self.received:
            return self.player.get_stone()
        else: 
            raise StoneException("Player has no stones")
    
    def set_conn(self, connection):
        return self.player.set_conn(connection)

    def is_connected(self): 
        return self.player.is_connected()
    
    def close_connection(self, shutdown):
        self.player.close_connection(shutdown)

    def make_move(self, boards: List):
        if not self.received: 
            raise PlayerStateViolation("Player asked to make a move but has not received stones")
        if self.ended: 
            raise PlayerStateViolation("Player asked to make a move but has already been notified of end game")
        return self.player.make_move(boards)

    def end_game(self):
        if self.ended:
            raise PlayerStateViolation("Player has already been notified of game end")
        self.ended = True
        self.received = False 
        return self.player.end_game()

class ProxyStateContractStrategyPlayer(ProxyStateContractPlayer):

    def __init__(self, player):
        super().__init__(player)
        self.has_strategy = False
    
    def set_strategy(self, strategy: PlayerStrategy):
        if self.has_strategy: 
            raise PlayerStateViolation("Strategy Player has already received a strategy")
        self.has_strategy = True
        self.player.set_strategy(strategy)

class ProxyTypeContractPlayer(AbstractPlayer):
    
    def __init__(self, player):
        self.player = player

    def register(self):
        register_resp = self.player.register()
        if not register_resp is False and not isinstance(register_resp, str):
            raise PlayerTypeError("Player returned a non-string object: {} as it's name".format(register_resp))
        return register_resp
        
    def get_name(self):
        name = self.player.get_name()
        if not isinstance(name, str):
            raise PlayerTypeError("Player returned a non-string object: {} as it's name".format(name))
        return name
    
    def receive_stones(self, stone: str):
        if not isinstance(stone, str):
            raise PlayerTypeError("Player received a non-string object: {} as it's stone".format(stone))
        if stone not in STONE: 
            raise PlayerTypeError("Player received an invalid stone: {}".format(stone))
        self.player.receive_stones(stone)
    
    def get_stone(self):
        stone = self.player.get_stone()
        if not isinstance(stone, str):
            raise PlayerTypeError("Player returned a non-string object: {} as it's stone".format(stone))
        if stone not in STONE:
            raise PlayerTypeError("Player returned the following invalid stone: {} as it's stone".format(stone))
        return stone

    def is_connected(self):
        return self.player.is_connected()

    def make_move(self, boards: List):
        if not isinstance(boards, list):
            raise PlayerTypeError("Player received non-list object: {} for make-a-move".format(boards))
        not_nested_list = any(not isinstance(b, list) for b in boards)
        if not_nested_list: 
            raise PlayerTypeError("Player should received a nested list object: {} in make-a-move".format(boards))
        return self.player.make_move(boards)

    def end_game(self):
        end_game_resp = self.player.end_game()         
        if not end_game_resp is False and not isinstance(end_game_resp, str):
            raise PlayerTypeError("Player returned a non-string object as it's end game message: {}".format(end_game_resp))
        return end_game_resp

class ProxyTypeContractConnectionPlayer(ProxyTypeContractPlayer):

    def __init__(self, player):
        super().__init__(player)
        self.player = player
    
    def set_conn(self, connection):
        if not isinstance(connection, socket):
            raise PlayerTypeError("Proxy Connection Player received a non socket object: {} as a connection".format(connection))
        self.player.set_conn(connection)
  
    def close_connection(self, shutdown):
        if not isinstance(shutdown, bool):
            raise PlayerTypeError("Proxy Player shutdown flag should be a boolean, instead: {}".format(shutdown))
        self.player.close_connection(shutdown)

class ProxyTypeContractStrategyPlayer(ProxyTypeContractPlayer):

    def __init__(self, player):
        super().__init__(player)
        self.player = player
    
    def set_strategy(self, strategy):
        if not isinstance(strategy, PlayerStrategy):
            raise PlayerTypeError("Strategy Player received a non strategy object: {} as a strategy".format(strategy))
        self.player.set_strategy(strategy)
    
class ProxyConnectionPlayer(AbstractPlayer):
    
    def _init__(self):
        self.name = ""
        self.stone = ""
        self.client_connected = False
        
    def set_conn(self, conn):
        self.conn = conn
        self.client_connected = True
    
    def register(self):
        super().register()
        self.name = self.send(["register"])
        return self.name

    def receive_stones(self, stone: str):
        super().receive_stones(stone)
        command = ["receive-stones"]
        command.append(stone)
        message = json.dumps(command)
        self.conn.sendall(message.encode())

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
    
    def close_connection(self, shutdown: bool):
        if shutdown: 
            self.conn.shutdown(1)
        self.conn.close()

    def send(self, message):
        #print("sent message", message)
        try:
            message = json.dumps(message)
            self.conn.sendall(message.encode("UTF-8"))
            resp = self.conn.recv(4096).decode("UTF-8")
            #print("received message", resp)
            if not resp:
                self.client_connected = False
                return False
            return resp
        except BrokenPipeError:
            print("remote player not connected")
            #self.client_connected = False
            return False

class RandomStrategyPlayer(AbstractPlayer):
    """
    Accepts a strategy and asks it to play
    """
    def __init__(self):
        super().__init__()
        self.strategy = None
    
    def set_strategy(self, strategy):
        self.strategy = strategy
        self.name = strategy.__class__.__name__
    
    def make_move(self, boards: List):
        return self.strategy.apply_strategy(boards, self.get_stone())


# class GUIPlayer(AbstractPlayer):
    
#     """
#     Starts a GUI so a human can play
#     """

#     def __init__(self):
#         super().__init__()
        
#         self.line_sprites = []
#         self.opposing_points = {}
#         self.player_points = {}
#         self.top_message = None
#         self.win = GraphWin('Alexis & Kelly\'s Go Game', WINDOW_WIDTH, WINDOW_HEIGHT)
#         self.win.setBackground(color_rgb(181, 171, 170))
#         self.window_open = True

#     def alert(self, message: str):
#         """
#         Input: str
#         Output: None
#         Description: Takes a message and changes the text of the "top_message" attribute

#         """
#         if not self.top_message:
#             self.top_message = Text(Point(HALF_WINDOW_WIDTH,TOP_OFFSET / 2), "")
#             self.top_message.setTextColor('black')
#             self.top_message.setSize(16)
#             self.top_message.draw(self.win)
            
#         self.top_message.setText(message)

#     def register(self):
#         super().register()
#         self.init_game()
#         return self.name

#     def receive_stones(self, color):
#         super().receive_stones(color)
#         self.notify_color()
#         self.opposing_stone = 'W' if self.stone == "B" else "B"
#         return

#     def make_move(self, boards: List):
#         self.draw_opponent_move(boards)
#         move = self.get_click_move(boards)
#         return move

#     def end_game(self):
#         """
#         Input: None
#         Output: None
#         Description: Show the 'GAME OVER' screen
#         """
#         try:
#             game_over_rect = Rectangle(Point(HALF_WINDOW_WIDTH - GAME_OVER_RECTANGLE , HALF_WINDOW_HEIGHT), \
#                                         Point(HALF_WINDOW_WIDTH + GAME_OVER_RECTANGLE , HALF_WINDOW_HEIGHT + 40))
#             game_over_rect.setFill('white')
#             game_over_rect.draw(self.win)
#             game_over_text = Text(game_over_rect.getCenter(), "GAME OVER")
#             game_over_text.setTextColor('black')
#             game_over_text.draw(self.win)
#             self.alert('Click anywhere to continue')
#             self.win.getMouse()
#             self.win.close()
#         except GraphicsError:
#             pass


#     def init_game(self):
#         """
#         Input: None
#         Output: None
#         Description: Builds the first screen the user sees to get their name
#         when done, it erases what it built and calls 'draw_board' and 'draw_pass'
#         """
#         sprites = []
        
#         message = Text(Point(HALF_WINDOW_WIDTH - TEXTBOX_WIDTH * 2, HALF_WINDOW_HEIGHT - 20), "Enter your name:")
#         message.setTextColor('black')
#         sprites.append(message)

#         inputBox = Entry(Point(HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT), TEXTBOX_WIDTH)
#         sprites.append(inputBox)

#         textAnchorPoint = inputBox.getAnchor()
#         rec_point1 = Point(textAnchorPoint.getX(), textAnchorPoint.getY() + 20)
#         rec_point2 = Point(textAnchorPoint.getX() + TEXTBOX_WIDTH * 4, textAnchorPoint.getY() + 40)
#         name_button = Rectangle(rec_point1, rec_point2)
#         name_button.setFill('white')
#         sprites.append(name_button)

#         name_button_text = Text(name_button.getCenter(), "Submit")
#         name_button_text.setTextColor('black')
#         sprites.append(name_button_text)

#         self.draw_sprites(sprites)
#         while(True):
#             inputStr = inputBox.getText()
#             click = self.win.checkMouse()
#             key = self.win.checkKey()
#             if (click and self.is_within_rectangle(rec_point1, rec_point2, click)) or \
#                 (key and key == 'Return'):
#                 break

#         self.name = inputStr
#         self.undraw_sprites(sprites)
#         self.draw_board()
#         self.draw_pass()

#     def draw_board(self):
#         """
#         Input: None
#         Output: None
#         Description: Draw the game board based on specs in the 'definitions' file
#         Stores all the "sprites" it drew in self.line_sprites for future deletion
#         """
#         #draw vertical lines
#         for x in range(BOARD_COLUMNS_MAX):
#             top_point = Point(LEFT_OFFSET + (SQUARE_SIZE * x), TOP_OFFSET)
#             bottom_point = Point(LEFT_OFFSET + (SQUARE_SIZE * x), TOP_OFFSET + BOARD_HEIGHT - SQUARE_SIZE)
#             ln = Line(top_point, bottom_point)
#             ln.setOutline('black')
#             ln.setWidth(3)
#             self.line_sprites.append(ln)

#         for y in range(BOARD_ROWS_MAX):
#             left_point = Point(LEFT_OFFSET, TOP_OFFSET + (SQUARE_SIZE * y))
#             right_point = Point(LEFT_OFFSET + BOARD_WIDTH - SQUARE_SIZE, TOP_OFFSET + (SQUARE_SIZE * y))
#             ln = Line(left_point, right_point)
#             ln.setOutline('black')
#             ln.setWidth(3)
#             self.line_sprites.append(ln)

#         self.draw_sprites(self.line_sprites)

#     def draw_pass(self):
#         """
#         Input: None
#         Output: None
#         Description: Draws the pass button with dimensions from the definitions file
#         """

#         left_corner = Point(LEFT_PASS_BUTTON, TOP_PASS_BUTTON)
#         right_corner = Point(RIGHT_PASS_BUTTON, BOTTOM_PASS_BUTTON)

#         pass_button = Rectangle(left_corner, right_corner)
#         pass_button.setFill(color_rgb(50, 75, 122))
#         pass_button.draw(self.win)

#         pass_center = pass_button.getCenter()
#         pass_text = Text(pass_center, 'PASS')
#         pass_text.setTextColor('white')
#         pass_text.setSize(15)
#         pass_text.draw(self.win)

#     def notify_color(self):
#         """
#         Input: None
#         Output: None
#         Description: Function to call alert method to display player name and stone
#         """

#         color = "WHITE"
#         if self.stone == "B":
#             color = "BLACK"

#         message = "Hello, " + self.name + "!" + "\nYou are the " + color + " stone."
#         self.alert(message)

#     def draw_opponent_move(self, boards):
#         """
#         Input: boards (list[list])
#         Output: None
#         Description: given at least two boards, uses the rulechecker to get the 
#         last move the opponent did. This move is then drawn onto the board
#         """

#         if len(boards) < 2:
#             return

#         # get the move that the opposing player just made
#         move = rulechecker.findAddedPoint(boards[1], boards[0])
#         self.alert("")
#         if move[0] == PASS_OUTPUT:
#             self.alert("Opponent passed")
#             return

#         # add that stone to the board
#         self.add_stone_to_board(move[1], self.opposing_points, move[0])
#         self.remove_stones(Board(boards[0]))

#     def get_click_move(self, boards):
#         """
#         Input: boards (list[list])
#         Output: point str
#         Description: Given the boards history, get the players input and 
#         draw it on the board. Call remove stones to show captures.
#         """
#         board = Board(boards[0])
#         while(True):
#             try:
#                 click = self.win.getMouse()
#                 return_point = self.pixels_to_move(click)
#                 print(return_point)
#                 if not return_point:
#                     continue
#                 if return_point != PASS_OUTPUT:
#                     try:
#                         new_board = board.place(self.stone, return_point)
#                         self.add_stone_to_board(return_point, self.player_points, self.stone)
#                     except (BoardPointException, BoardException):
#                         continue
#                     self.remove_stones(Board(new_board))
#                 break
#             except GraphicsError:
#                 return "close"
#         return return_point

#     def pixels_to_move(self,mouse_point: Point):
#         """
#         Input: graphics.Point
#         Output: point string in the format 'x-y' or PASS_OUTPUT or False
#         Description: Takes a coordinate from the mouse click and replies with the
#         correct point on the board it clicked.
#         """    

#         pass_rectangle_top_right = Point(LEFT_PASS_BUTTON, TOP_PASS_BUTTON)
#         pass_rectangle_bottom_left = Point(RIGHT_PASS_BUTTON, BOTTOM_PASS_BUTTON)
#         if self.is_within_rectangle(pass_rectangle_top_right, pass_rectangle_bottom_left, mouse_point):
#             return PASS_OUTPUT

#         x = mouse_point.getX()
#         y = mouse_point.getY()

#         x_index = (x - LEFT_OFFSET) / SQUARE_SIZE
#         y_index = (y - TOP_OFFSET) / SQUARE_SIZE

#         if x_index % 1 < .2 or x_index % 1 > .8:
#             x = round(x_index)
#             if y_index % 1 < .2 or y_index % 1 > .8:
#                 y = round(y_index)
#                 return str(x+1) + "-" + str(y+1)
#         return False

#     def add_stone_to_board(self, point, drawn_points, color):
#         """
#         Input: str, dict, str
#         Output: None
#         Description: given a string point, it's drawn points, and the color stone,
#         add the string point to the board
#         """
#         if point not in drawn_points:
#             color = 'black' if color == 'B' else 'white'
#             bp = BoardPoint(point)
#             aCircle = Circle(self.index_to_pixels(bp.x_ind, bp.y_ind), STONE_RADIUS)
#             aCircle.setFill(color)
#             drawn_points[point] = aCircle
#             aCircle.draw(self.win)

#     def remove_stones(self, board):
#         """
#         Input: Board
#         Output: None
#         Description: Given the current board, look at the stones that are
#         currently drawn on and determine if any need to be undrawn
#         """
        
#         remove_opponent, remove_player = self.get_point_sprites_to_undraw(board)
#         if remove_opponent:
#             self.undraw_sprites([self.opposing_points[x] for x in remove_opponent])
#             [self.opposing_points.pop(key) for key in remove_opponent]
#         if remove_player:
#             self.undraw_sprites([self.player_points[x] for x in remove_player])
#             [self.player_points.pop(key) for key in remove_player]

#     def get_point_sprites_to_undraw(self, board):
#         """
#         Input: Board
#         Output: list of string points
#         Description: Given a board, look at the drawn points for opponent and 
#         current players and determine if any of them need to be undrawn
#         """
    
#         #lists of points that are on the current board
#         current_opponent = board.get_points(self.opposing_stone)
#         current_player = board.get_points(self.stone)

#         prev_opponent = self.opposing_points.keys()
#         prev_player = self.player_points.keys()

#         removed_opponent = prev_opponent - current_opponent
#         removed_player = prev_player - current_player

#         return [x for x in removed_opponent], [x for x in removed_player]


#     def undraw_sprites(self,sprites):
#         """
#         Input: list
#         Output: None
#         Description: Given list of sprites, undraw them
#         """
#         if sprites:
#             for sprite in sprites:
#                 sprite.undraw()

#     def draw_sprites(self, sprites):
#         """
#         Input: list
#         Output: None
#         Description: Given list of sprites, draw them in the window
#         """
#         if sprites:
#             for sprite in sprites:
#                 sprite.draw(self.win)

#     def index_to_pixels(self, x_ind, y_ind):
#         """
#         Input: integer, integer
#         Output: graphics.Point
#         Description: Given an x and y coordinate in the GO coordinate system,
#         return that point in the screen pixels
#         """
#         return Point(LEFT_OFFSET + (SQUARE_SIZE * x_ind), TOP_OFFSET + (SQUARE_SIZE * y_ind))


#     def is_within_rectangle(self, top_left, bottom_right, point):
#         """
#         Input: graphics.Point, graphics.Point, graphics.Point
#         Output: Boolean
#         Description: Given the top left point of a rectangle and the bottom right 
#         point of a rectangle, return whether point is inside that rectangle or not
#         """
#         left = top_left.getX()
#         top = top_left.getY()
#         bottom = bottom_right.getY()
#         right = bottom_right.getX()

#         x = point.getX()
#         y = point.getY()

#         if x >= left and x <= right and y <= bottom and y >= top:
#             return True
#         return False