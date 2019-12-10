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

class GUIPlayer():
    def __init__(self):
        self.buffer = 131072
        netData = readConfig(GO_CONFIG_PATH)[0]
        self.player = None
        self.win = GraphWin('Alexis & Kelly\'s Go Game', WINDOW_WIDTH, WINDOW_HEIGHT)
        self.win.setBackground(color_rgb(181, 171, 170))
        self.connect_socket(netData)
        self.start_client()
        
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
        #print("starting client")
        #### USE FACTORY
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

    def parse_command(self, command):
        if command[0] == "register":
            self.init_game()
            return self.player_name
    
        elif command[0] == "receive-stones":
            try:
                self.stone = command[1]
                return
            except (StoneException, AttributeError):
                return CRAZY_GO
          
        elif command[0] == "make-a-move":
            try:
                if not self.player_name or self.stone == "":
                    return CRAZY_GO
                if not checkhistory(command[1], self.stone): 
                    return ILLEGAL_HISTORY_MESSAGE
                return self.draw_board(command[1])   
            except (StoneException, BoardException, IndexError):
                return CRAZY_GO

        elif command[0] == "end-game":
            try:
                return "OK"
            except PlayerException:
                return CRAZY_GO

    def pixels_to_index(self,mouse_point):
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
        return Point(LEFT_OFFSET + (SQUARE_SIZE * x_ind), TOP_OFFSET + (SQUARE_SIZE * y_ind))

    def is_within_rectangle(self, top_left, bottom_right, point):
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
        
        message = Text(Point(HALF_WINDOW_WIDTH - TEXTBOX_WIDTH * 2, HALF_WINDOW_HEIGHT - 20), "Enter your name:")
        message.setTextColor('black') 
        message.draw(self.win)

        inputBox = Entry(Point(HALF_WINDOW_WIDTH, HALF_WINDOW_HEIGHT), TEXTBOX_WIDTH)
        inputBox.draw(self.win)

        textAnchorPoint = inputBox.getAnchor()
        rec_point1 = Point(textAnchorPoint.getX(), textAnchorPoint.getY() + 20)
        rec_point2 = Point(textAnchorPoint.getX() + TEXTBOX_WIDTH * 4, textAnchorPoint.getY() + 40)
        name_button = Rectangle(rec_point1, rec_point2)
        name_button.setFill('white')
        name_button.draw(self.win)

        name_button_text = Text(name_button.getCenter(), "Submit")
        name_button_text.setTextColor('black')
        name_button_text.draw(self.win)

        while(True):
            inputStr = inputBox.getText()
            click = self.win.checkMouse()
            if click and self.is_within_rectangle(rec_point1, rec_point2, click):
                break

        self.player_name = inputStr
        message.undraw()
        inputBox.undraw()
        name_button.undraw()
        name_button_text.undraw()
        #draw_board(win)

    def draw_board(self, board):
        board = Board(board[0])
        #draw vertical lines
        for x in range(BOARD_COLUMNS_MAX):
            top_point = Point(LEFT_OFFSET + (SQUARE_SIZE * x), TOP_OFFSET)
            bottom_point = Point(LEFT_OFFSET + (SQUARE_SIZE * x), TOP_OFFSET + BOARD_HEIGHT - SQUARE_SIZE)
            ln = Line(top_point, bottom_point)
            ln.setOutline('black')
            ln.draw(self.win)

        for y in range(BOARD_ROWS_MAX):
            left_point = Point(LEFT_OFFSET, TOP_OFFSET + (SQUARE_SIZE * y))
            right_point = Point(LEFT_OFFSET + BOARD_WIDTH - SQUARE_SIZE, TOP_OFFSET + (SQUARE_SIZE * y))
            ln = Line(left_point, right_point)
            ln.setOutline('black')
            ln.draw(self.win)

        white_points = board.get_points("W")
        for point in white_points:
            bp = BoardPoint(point)
            aCircle = Circle(self.index_to_pixels(bp.x_ind, bp.y_ind), STONE_RADIUS)
            aCircle.setFill('white')
            aCircle.draw(self.win)

        black_points = board.get_points("B")
        for point in black_points:
            bp = BoardPoint(point)
            aCircle = Circle(self.index_to_pixels(bp.x_ind, bp.y_ind), STONE_RADIUS)
            aCircle.setFill('black')
            aCircle.draw(self.win)

        while(True):
            click = self.win.checkMouse()
            
            if click:
                return_point = self.pixels_to_index(click)
                if return_point:
                    break
        print(return_point)
        return return_point
        

if __name__ == "__main__":       
    GUIPlayer()