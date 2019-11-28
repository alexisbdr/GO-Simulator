import sys
import json
from json import JSONDecodeError
from rulechecker import *
from utilities import readConfig
from utilities import readJSON
from player_factory import PlayerFactory
import time
import socket
from exceptions import StoneException
from exceptions import BoardException
from exceptions import PlayerException

class RemoteReferee: 
    
    buffer = 131072

    def __init__(self):
        netData = readConfig(GO_CONFIG_PATH)[0]
        self.player = None
        self.connect_socket(netData)
        self.start_client()
        
    def connect_socket(self, data: dict):
        host = data['IP']
        port = data['port']
        #print(host)
        #print(port)
        connected = False
        #Connect
        iter = 0
        #print("trying to connect")
        while not connected:
            try: 
                #print("Trying to connect")
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((host, port))
                #print("connected")
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
                print(resp)
                resp = resp.decode("UTF-8")
                print(resp)
            except ConnectionResetError:
                self.client_socket.close()
                break
            #there is nothing coming from the server, so it has disconnected
            if not resp:
                #self.client_socket.shutdown(socket.SHUT_WR)
                self.client_socket.close()
                #print("Client closed")
                break
            elif resp: 
                resp_json = readJSON(resp)
                output = self.parse_command(resp_json[0])
                #print(output)
                if output == "close":
                    self.client_socket.shutdown(1)
                    self.client_socket.close()
                    break
                #print(output)
                self.client_socket.send(str.encode(output))
            

    def parse_command(self, command):
        if command[0] == "register":
            if self.player:
                return CRAZY_GO
            self.player = PlayerFactory(remote=True).create()
            self.player.register()
            return self.player.get_name()
    
        elif command[0] == "receive-stones":
            #return "close"
            try:
                self.player.set_stone(command[1])
                return ' '
            except (StoneException, AttributeError):
                return CRAZY_GO
          
        elif command[0] == "make-a-move":
            try:
                if not self.player or self.player.get_stone() == "" or \
                    self.player.ended:
                    return CRAZY_GO
                if not checkhistory(command[1], self.player.get_stone()): 
                    return ILLEGAL_HISTORY_MESSAGE
                return self.player.make_move(command[1])   
            except (StoneException, BoardException, IndexError):
                return CRAZY_GO

        elif command[0] == "end-game":
            #return " "
            try:
                return self.player.end_game()
            except PlayerException:
                return CRAZY_GO

if __name__ == "__main__":
    RemoteReferee()
