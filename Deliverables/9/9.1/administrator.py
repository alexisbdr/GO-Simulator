import socket
import sys
from utilities import readJSON
from utilities import nextPowerOf2
from typing import List

from definitions import *
from player_factory import PlayerFactory
from tournament import League
from tournament import Cup
import time
import random
from referee import Referee
import json
from threading import Thread

class Administrator:
    
    def __init__(self, tournament: str, num_players: str):
        self.check_inputs(tournament, num_players)
        self.load_config()
        self.get_players()
        self.start_tournament()

    def check_inputs(self, tournament: str, num_players: str):
        if tournament == "-league" or tournament != "-cup":
            raise Exception("Invalid tournament input")
        else: self.tournament = tournament.strip("-")
        try: 
            self.num_players = int(num_players)
        except ValueError as e: 
            raise Exception("Number players should be an integer")
        print(self.tournament, self.num_players)
        
    def load_config(self):
        config_file = open(GO_CONFIG_PATH, 'r')
        config_file = config_file.read()
        netData = readJSON(config_file)
        netData = netData[0]
        self.host = netData['IP']
        self.port = netData['port']
        self.default_player_path = netData['default-player']
    
    def get_players(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host , self.port))
        self.players = []
        print("getting players")
        while self.num_players != len(self.players):
            print("started loop")
            self.server_socket.listen()
            conn, addr = self.server_socket.accept()
            print("new player on conn: ",conn)
            proxy_player = PlayerFactory(connection=conn).create()
            self.players.append(proxy_player)
            print(self.players)
        self.make_players()
    
    def make_players(self):
        self.num_players = nextPowerOf2(self.num_players)
        while self.num_players != len(self.players):
            default_player = PlayerFactory(path=self.default_player_path).create()
            self.players.append(default_player)
            print("made a new player")
        self.register_players()

    def register_players(self):
        print("registering")
        for p in range(len(self.players)):
            resp = self.players[p].register()
            if not resp:
                #Replace player that doesn't register with a default player
                self.players[p] = PlayerFactory(path=self.default_player_path).create()

    def start_tournament(self):
        print("starting tournament")
        if self.tournament == "cup":
            tournament_results = Cup(self.players).get_results()
        elif self.tournament == "league":
            tournament_results = League(self.players, self.default_player_path).get_results()
        self.print_results(tournament_results)
        self.close_connection()

    def print_results(self, results: dict):
        print(json.dumps(results))
        
    def close_connection(self):
        for player in self.players:
            if player.is_connected:
                player.conn.shutdown(1)
                player.conn.close()
        #shutdown the server connection
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) != 3:
        raise Exception("Incorrect number of command line arguments")
    tournament = sys.argv[1]
    num_players = sys.argv[2]
    Administrator(tournament, num_players)