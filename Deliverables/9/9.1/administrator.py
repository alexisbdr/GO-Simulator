import socket
import sys
from utilities import readJSON
from utilities import nextPowerOf2
from typing import List

from definitions import *
from player_factory import PlayerFactory
import time
import random
from referee import Referee
import json

class Administrator:
    
    def __init__(self, tournament: str, num_players: str):
        self.check_inputs(tournament, num_players)
        self.load_config()
        self.get_remote_players()

    def check_inputs(self, tournament: str, num_players: str):
        if tournament == "-league" or tournament != "-cup":
            raise Exception("Invalid tournament input")
        else: self.tournament = tournament.strip("-")
        try: 
            self.num_players = int(num_players)
        except ValueError as e: 
            raise Exception("Number players should be an integer")
        
    def load_config(self):
        config_file = open(GO_CONFIG_PATH, 'r')
        config_file = config_file.read()
        netData = readJSON(config_file)
        netData = netData[0]
        self.host = netData['IP']
        self.port = netData['port']
        self.default_player_path = netData['default-player']
    
    def get_remote_players(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host , self.port))
        self.server_socket.listen(self.num_players)
        self.players = []
        while True: 
            conn, addr = self.server_socket.accept()
            proxy_player = PlayerFactory(connection=conn).create()
            self.players.append(proxy_player)
    
    def make_players(self):
        self.num_players = nextPowerOf2(self.num_players)
        while self.num_players != len(self.players):
            default_player = PlayerFactory(path=self.default_player_path).create()
            self.players.append(default_player)
        self.register_players()

    def register_players(self):
        for p in range(len(self.players)):
            resp = self.players[p].register()
            if not resp:
                self.players[p] = None
        

                

    def start_tournament(self):
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

if __name__ == "__main__":
    cmdline = sys.argv
    if len(cmdline) != 2:
        raise Exception("Incorrect number of command line arguments")
    tournament = cmdline[0]
    num_players = cmdline[1]
    Administrator(tournament, num_players)