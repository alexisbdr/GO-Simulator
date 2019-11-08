import sys
import json
from json import JSONDecodeError
from rulechecker import *
from utilities import readConfig, readJSON
from player import Player
import time
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
        print(host)
        print(port)
        connected = False
        #Connect
        
        while not connected:
            try: 
                print("Trying to connect")
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((host, port))
                connected = True
            except ConnectionRefusedError:
                self.client_socket.close()
                time.sleep(2)
                continue
    
    def start_client(self):
        #### USE FACTORY
        self.player = Player()
        while True: 
            resp = self.client_socket.recv(self.buffer) 
            if resp == "close":
                self.client_socket.close()
                print("Client closed")
                break
            elif resp: 
                resp_json = readJSON(resp.decode("UTF-8"))
                output = self.parse_command(resp_json[0])
                self.client_socket.send(str.encode(output))

    def parse_command(self, command):
        if command[0] == "register":
            return self.player.get_name()
    
        elif command[0] == "receive-stones":
            self.player.set_color(command[1])
            return 'RECEIVE'
        
        elif command[0] == "make-a-move":
            if not checkhistory(command[1], self.player.get_color()): 
                return ILLEGAL_HISTORY_MESSAGE
            return self.player.make_move_two(command[1])
        else:
            return CRAZY_GO


if __name__ == "__main__":
    RemoteReferee()
