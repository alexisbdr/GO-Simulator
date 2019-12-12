from graphics import *
from definitions import *

from referee import Referee
from board import Board, BoardPoint
from player import AbstractPlayer
import socket
from rulechecker import *
from utilities import readConfig
from utilities import readJSON
from player_factory import PlayerFactory
import time
from exceptions import StoneException
from exceptions import BoardException
from exceptions import PlayerException
import rulechecker

class GUIPlayer():
    def __init__(self):
        self.buffer = 131072
        self.line_sprites = []
        self.opposing_points = {}
        self.player_points = {}
        self.accepting_click = False
        self.top_message = None
        netData = readConfig(GO_CONFIG_PATH)[0]
        self.player = None
        self.win = GraphWin('Alexis & Kelly\'s Go Game', WINDOW_WIDTH, WINDOW_HEIGHT)
        self.win.setBackground(color_rgb(181, 171, 170))
        self.connect_socket(netData)
        self.start_client()

    def alert(self, message: str):
        """
        Input: str
        Output: None
        Description: Takes a message and changes the text of the "top_message" attribute

        """
        if not self.top_message:
            self.top_message = Text(Point(HALF_WINDOW_WIDTH,TOP_OFFSET / 2), "")
            self.top_message.setTextColor('black')
            self.top_message.setSize(16)
            self.top_message.draw(self.win)
            
        self.top_message.setText(message)
        
    def connect_socket(self, data: dict):
        host = data['IP']
        port = data['port']
        connected = False
        iter = 0
        while not connected:
            try: 
                print('trying to connect')
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((host, port))
                print('connected')
                connected = True
            except ConnectionRefusedError:
                iter += 1
                if iter == 20:
                    #see here
                    break
                self.client_socket.close()
                time.sleep(2)
                continue
    
    def start_client(self):
        while True:
            try:
                resp = self.client_socket.recv(self.buffer) 
                resp = resp.decode("UTF-8")
            except ConnectionResetError:
                self.client_socket.close()
                break
            #there is nothing coming from the server, so it has disconnected
            if not resp:
                self.client_socket.close()
                break
            elif resp: 
                resp_json = readJSON(resp)
                output = self.parse_command(resp_json[0])
                if not output:
                    continue
                if output == "close":
                    self.client_socket.shutdown(1)
                    self.client_socket.close()
                    break
                self.client_socket.send(str.encode(output))

    def parse_command(self, command:str):
        """
            Input: str
            Output: str or None
            Description: reads a command and passes it along to the 
            correct method call. 
        """
        if command[0] == "register":
            self.init_game()
            return self.player_name
    
        elif command[0] == "receive-stones":
            try:
                self.stone = command[1]
                self.notify_color()
                self.opposing_stone = 'W' if self.stone == 'B' else 'B'
                return
            except (StoneException, AttributeError):
                return CRAZY_GO
          
        elif command[0] == "make-a-move":
            try:
                if not self.player_name or self.stone == "":
                    return CRAZY_GO
                if not checkhistory(command[1], self.stone): 
                    return ILLEGAL_HISTORY_MESSAGE
                self.draw_opponent_move(command[1])
                move = self.make_move(command[1])
                return move
            except (StoneException, BoardException, IndexError):
                return CRAZY_GO

        elif command[0] == "end-game":
            try:
                self.end_game()
                return "OK"
            except PlayerException:
                return CRAZY_GO

    def pixels_to_move(self,mouse_point: Point):
        """
        Input: graphics.Point
        Output: point string in the format 'x-y' or PASS_OUTPUT or False
        Description: Takes a coordinate from the mouse click and replies with the
        correct point on the board it clicked.
        """    

        pass_rectangle_top_right = Point(LEFT_PASS_BUTTON, TOP_PASS_BUTTON)
        pass_rectangle_bottom_left = Point(RIGHT_PASS_BUTTON, BOTTOM_PASS_BUTTON)
        if self.is_within_rectangle(pass_rectangle_top_right, pass_rectangle_bottom_left, mouse_point):
            return PASS_OUTPUT

        x = mouse_point.getX()
        y = mouse_point.getY()

        x_index = (x - LEFT_OFFSET) / SQUARE_SIZE
        y_index = (y - TOP_OFFSET) / SQUARE_SIZE

        if x_index % 1 < .2 or x_index % 1 > .8:
            x = round(x_index)
            if y_index % 1 < .2 or y_index % 1 > .8:
                y = round(y_index)
                return str(x+1) + "-" + str(y+1)
        return False

    def index_to_pixels(self, x_ind, y_ind):
        """
        Input: integer, integer
        Output: graphics.Point
        Description: Given an x and y coordinate in the GO coordinate system,
        return that point in the screen pixels
        """
        return Point(LEFT_OFFSET + (SQUARE_SIZE * x_ind), TOP_OFFSET + (SQUARE_SIZE * y_ind))

    def is_within_rectangle(self, top_left, bottom_right, point):
        """
        Input: graphics.Point, graphics.Point, graphics.Point
        Output: Boolean
        Description: Given the top left point of a rectangle and the bottom right 
        point of a rectangle, return whether point is inside that rectangle or not
        """
        left = top_left.getX()
        top = top_left.getY()
        bottom = bottom_right.getY()
        right = bottom_right.getX()

        x = point.getX()
        y = point.getY()

        if x >= left and x <= right and y <= bottom and y >= top:
            return True
        return False

    def init_game(self):
        """
        Input: None
        Output: None
        Description: Builds the first screen the user sees to get their name
        when done, it erases what it built and calls 'draw_board' and 'draw_pass'
        """
        sprites = []
        
        message = Text(Point(HALF_WINDOW_WIDTH - TEXTBOX_WIDTH * 2, HALF_WINDOW_HEIGHT - 20), "Enter your name:")
        message.setTextColor('black')
        sprites.append(message)

        inputBox = Entry(Point(HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT), TEXTBOX_WIDTH)
        sprites.append(inputBox)

        textAnchorPoint = inputBox.getAnchor()
        rec_point1 = Point(textAnchorPoint.getX(), textAnchorPoint.getY() + 20)
        rec_point2 = Point(textAnchorPoint.getX() + TEXTBOX_WIDTH * 4, textAnchorPoint.getY() + 40)
        name_button = Rectangle(rec_point1, rec_point2)
        name_button.setFill('white')
        sprites.append(name_button)

        name_button_text = Text(name_button.getCenter(), "Submit")
        name_button_text.setTextColor('black')
        sprites.append(name_button_text)

        self.draw_sprites(sprites)
        while(True):
            inputStr = inputBox.getText()
            click = self.win.checkMouse()
            key = self.win.checkKey()
            if (click and self.is_within_rectangle(rec_point1, rec_point2, click)) or \
                (key and key == 'Return'):
                break

        self.player_name = inputStr
        self.undraw_sprites(sprites)
        self.draw_board()
        self.draw_pass()

    def draw_board(self):
        """
        Input: None
        Output: None
        Description: Draw the game board based on specs in the 'definitions' file
        Stores all the "sprites" it drew in self.line_sprites for future deletion
        """
        #draw vertical lines
        for x in range(BOARD_COLUMNS_MAX):
            top_point = Point(LEFT_OFFSET + (SQUARE_SIZE * x), TOP_OFFSET)
            bottom_point = Point(LEFT_OFFSET + (SQUARE_SIZE * x), TOP_OFFSET + BOARD_HEIGHT - SQUARE_SIZE)
            ln = Line(top_point, bottom_point)
            ln.setOutline('black')
            ln.setWidth(3)
            self.line_sprites.append(ln)

        for y in range(BOARD_ROWS_MAX):
            left_point = Point(LEFT_OFFSET, TOP_OFFSET + (SQUARE_SIZE * y))
            right_point = Point(LEFT_OFFSET + BOARD_WIDTH - SQUARE_SIZE, TOP_OFFSET + (SQUARE_SIZE * y))
            ln = Line(left_point, right_point)
            ln.setOutline('black')
            ln.setWidth(3)
            self.line_sprites.append(ln)

        self.draw_sprites(self.line_sprites)

    def notify_color(self):
        """
        Input: None
        Output: None
        Description: Function to call alert method to display player name and stone
        """

        color = "WHITE"
        if self.stone == "B":
            color = "BLACK"

        message = "Hello, " + self.player_name + "!" + "\nYou are the " + color + " stone."
        self.alert(message)

    
    def draw_pass(self):
        """
        Input: None
        Output: None
        Description: Draws the pass button with dimensions from the definitions file
        """

        left_corner = Point(LEFT_PASS_BUTTON, TOP_PASS_BUTTON)
        right_corner = Point(RIGHT_PASS_BUTTON, BOTTOM_PASS_BUTTON)

        pass_button = Rectangle(left_corner, right_corner)
        pass_button.setFill(color_rgb(50, 75, 122))
        pass_button.draw(self.win)

        pass_center = pass_button.getCenter()
        pass_text = Text(pass_center, 'PASS')
        pass_text.setTextColor('white')
        pass_text.setSize(15)
        pass_text.draw(self.win)


    def draw_opponent_move(self, boards):
        """
        Input: boards (list[list])
        Output: None
        Description: given at least two boards, uses the rulechecker to get the 
        last move the opponent did. This move is then drawn onto the board
        """

        if len(boards) < 2:
            return

        # get the move that the opposing player just made
        move = rulechecker.findAddedPoint(boards[1], boards[0])
        self.alert("")
        if move[0] == PASS_OUTPUT:
            self.alert("Opponent passed")
            return

        # add that stone to the board
        self.add_stone_to_board(move[1], self.opposing_points, move[0])
        self.remove_stones(Board(boards[0]))

    def make_move(self, boards):
        """
        Input: boards (list[list])
        Output: point str
        Description: Given the boards history, get the players input and 
        draw it on the board. Call remove stones to show captures.
        """
        board = Board(boards[0])
        try:
            click = self.win.getMouse()
            return_point = self.pixels_to_move(click)
            if return_point != PASS_OUTPUT:
                self.add_stone_to_board(return_point, self.player_points, self.stone)
                new_board = board.place(self.stone, return_point)
                self.remove_stones(Board(new_board))
            return return_point
        except GraphicsError:
            return "close"
    
    def remove_stones(self, board):
        """
        Input: Board
        Output: None
        Description: Given the current board, look at the stones that are
        currently drawn on and determine if any need to be undrawn
        """
        
        remove_opponent, remove_player = self.get_point_sprites_to_undraw(board)
        if remove_opponent:
            self.undraw_sprites([self.opposing_points[x] for x in remove_opponent])
            [self.opposing_points.pop(key) for key in remove_opponent]
        if remove_player:
            self.undraw_sprites([self.player_points[x] for x in remove_player])
            [self.player_points.pop(key) for key in remove_player]


    def add_stone_to_board(self, point, drawn_points, color):
        """
        Input: str, dict, str
        Output: None
        Description: given a string point, it's drawn points, and the color stone,
        add the string point to the board
        """
        if point not in drawn_points:
            color = 'black' if color == 'B' else 'white'
            bp = BoardPoint(point)
            aCircle = Circle(self.index_to_pixels(bp.x_ind, bp.y_ind), STONE_RADIUS)
            aCircle.setFill(color)
            drawn_points[point] = aCircle
            aCircle.draw(self.win)

    
    
    def get_point_sprites_to_undraw(self, board):
        """
        Input: Board
        Output: list of string points
        Description: Given a board, look at the drawn points for opponent and 
        current players and determine if any of them need to be undrawn
        """
    
        #lists of points that are on the current board
        current_opponent = board.get_points(self.opposing_stone)
        current_player = board.get_points(self.stone)

        prev_opponent = self.opposing_points.keys()
        prev_player = self.player_points.keys()

        removed_opponent = prev_opponent - current_opponent
        removed_player = prev_player - current_player

        return [x for x in removed_opponent], [x for x in removed_player]


    def end_game(self):
        """
        Input: None
        Output: None
        Description: Show the 'GAME OVER' screen
        """
        game_over_rect = Rectangle(Point(HALF_WINDOW_WIDTH - GAME_OVER_RECTANGLE , HALF_WINDOW_HEIGHT), \
                                    Point(HALF_WINDOW_WIDTH + GAME_OVER_RECTANGLE , HALF_WINDOW_HEIGHT + 40))
        game_over_rect.setFill('white')
        game_over_rect.draw(self.win)
        game_over_text = Text(game_over_rect.getCenter(), "GAME OVER")
        game_over_text.setTextColor('black')
        game_over_text.draw(self.win)
        self.alert('Click anywhere to continue')
        try:
            self.win.getMouse()
            self.win.close()
        except GraphicsError:
            pass
        
    def undraw_sprites(self,sprites):
        """
        Input: list
        Output: None
        Description: Given list of sprites, undraw them
        """
        if sprites:
            for sprite in sprites:
                sprite.undraw()

    def draw_sprites(self, sprites):
        """
        Input: list
        Output: None
        Description: Given list of sprites, draw them in the window
        """
        if sprites:
            for sprite in sprites:
                sprite.draw(self.win)

if __name__ == "__main__":       
    GUIPlayer()