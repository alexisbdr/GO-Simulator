import socket
import sys
from utilities import readJSON
from typing import List

from definitions import *
from player_factory import PlayerFactory
import time
import random
from referee import Referee
import json

class Administrator:
    
    def __init__(self):
        self.load_config()
        self.create_server_conn()
    
    def load_config(self):
        config_file = open(GO_CONFIG_PATH, 'r')
        config_file = config_file.read()
        netData = readJSON(config_file)
        netData = netData[0]
        self.host = netData['IP']
        self.port = netData['port']
        self.default_player_path = netData['default-player']
    
    def create_server_conn(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host , self.port))
        self.server_socket.listen(1)
        self.started = False
        self.conn, self.addr = self.server_socket.accept()
        self.proxy_player = PlayerFactory(connection=self.conn).create()
        self.default_player = PlayerFactory(path=self.default_player_path).create()
        self.start_game()
        

    def start_game(self):
        
        choice = random.randint(0, 1)
        if choice:
            referee = Referee(self.proxy_player, self.default_player)
        else:
            referee = Referee(self.default_player, self.proxy_player)
       # referee = Referee(self.proxy_player, self.default_player) if choice else Referee(self.default_player, self.proxy_player)
        print(json.dumps(referee.get_winner()))
        self.close_connection()
        
    def close_connection(self):
        if self.proxy_player.is_connected():
            self.conn.shutdown(1)
            self.conn.close()
        else:
            self.conn.close()


Administrator()