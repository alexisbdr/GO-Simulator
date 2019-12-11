import socket
import sys
from utilities import readJSON
from utilities import nextPowerOf2
from typing import List

from definitions import *
from player_factory import PlayerFactory
from tournament import Tournament
import time
import random
from referee import Referee
import json
from threading import Thread
import operator

class Administrator:
    
    def __init__(self, tournament: str, num_players: str, socket, path):
        self.server_socket = socket
        self.default_player_path = path
        self.check_inputs(tournament, num_players)
        self.get_connections()
        self.start_tournament()

    def check_inputs(self, tournament: str, num_players: str):
        if tournament == "league" or tournament == "cup":
            self.tournament = tournament
        else: raise Exception("Invalid tournament input")
        try: 
            self.num_players = int(num_players)
        except ValueError as e: 
            raise Exception("Number players should be an integer")
        #print(self.tournament, self.num_players)
        
    def get_connections(self):
        connections = []
        self.players = []
        print("getting players")
        self.server_socket.listen(self.num_players)
        while self.num_players != len(self.players):
            #print("started loop")
            conn, addr = self.server_socket.accept()
            proxy_player = PlayerFactory(connection=conn).create()
            self.players.append(proxy_player)
            print("new player on conn: ",conn)
            #connections.append(conn)
            #print(self.players)
        self.make_players()
        self.server_socket.close()
       
    
    def make_players(self):
        #self.players = []
        self.num_players = nextPowerOf2(self.num_players)
        #for conn in connection_list:
            #proxy_player = PlayerFactory(connection=conn).create()
            #self.players.append(proxy_player)
        while self.num_players != len(self.players):
            default_player = PlayerFactory(path=self.default_player_path).create()
            self.players.append(default_player)
            #print("made a new player")
        self.register_players()

    def register_players(self):
        #print("registering")
        for p in range(len(self.players)):
            resp = self.players[p].register()
            if not resp:
                #Replace player that doesn't register with a default player
                self.players[p] = PlayerFactory(path=self.default_player_path).create()
                self.players[p].register()

    def start_tournament(self):
        #print("starting tournament")
        run_tournament = Tournament(self.tournament, self.players, self.default_player_path)
        participating_players = run_tournament.get_participating_players()
        for p in participating_players:
            self.close_connection(p)

        run_tournament.print_results()      

        
    def close_connection(self, player):
        if player.is_connected():
            print("disconnecting player", player)
            try:
                player.conn.shutdown(1)
                player.conn.close()
            except (OSError, BrokenPipeError) as e:
                player.conn.close()
                print("player already disconnected, error: ", e)
                return
        return

def load_config():
    config_file = open(GO_CONFIG_PATH, 'r')
    config_file = config_file.read()
    netData = readJSON(config_file)
    netData = netData[0]
    host = netData['IP']
    port = netData['port']
    default_player_path = netData['default-player']
    return host, port, default_player_path

def create_socket(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host , port))
    return server_socket

if __name__ == "__main__":
    host, port, path = load_config()
    socket = create_socket(host, port)
    #print(sys.argv)
    if len(sys.argv) != 3:
        raise Exception("Incorrect number of command line arguments")
    tournament = sys.argv[1].strip("-")
    num_players = sys.argv[2]
    Administrator(tournament, num_players, socket, path)