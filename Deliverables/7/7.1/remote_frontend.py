import sys
import json
from json import JSONDecodeError
from rulechecker import *
from utlities import readConfig, readJSON
from player import Player

import socket

class RemoteReferee: 
    
    buffer = 131072

    def __init__(self):
        netData = readConfig(GO_CONFIG_PATH)[0]
        self.connect_socket(netData)
        self.start_client()
        
    def connect_socket(self, data: dict):
        host = data['IP']
        port = data['port']
        #Connect
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    
    def start_client(self):
        #### USE FACTORY
        self.player = Player()
        while True: 
            resp = self.client_socket.recv(self.buffer) 
            if resp: 
                resp_json = readJSON(resp.decode("UTF-8"))
                output = self.parse_command(resp_json)
                self.client_socket.send(str.encode(json.dumps(output)))


    def parse_command(self, command):
        if command[0] == "register":
            return self.player.get_name()
    
        elif command[0] == "receive-stones":
            self.player.set_color(command[1])
            return None
        
        elif command[0] == "make-a-move":
            if not checkhistory(command[1], self.player.get_color()): 
                return ILLEGAL_HISTORY_MESSAGE
            return self.player.make_move_two(command[1])
        else:
            return CRAZY_GO


if __name__ == "__main__":
    RemoteReferee()
