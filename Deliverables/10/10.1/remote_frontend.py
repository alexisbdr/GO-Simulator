import sys
import json
from rulechecker import *
from utilities import readConfig
from utilities import readJSON
from player_factory import PlayerFactory
import time
import socket
from exceptions import StoneException
from exceptions import BoardException
from exceptions import PlayerException
from exceptions import PlayerStateViolation, PlayerTypeError

class RemoteReferee: 
    
    buffer = 131072

    def __init__(self):
        netData = readConfig(GO_CONFIG_PATH)[0]
        self.player = PlayerFactory(remote=True).create()
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
                resp = resp.decode("UTF-8")
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
                print(output)
                if not output:
                    continue
                if output == "close":
                    self.client_socket.shutdown(1)
                    self.client_socket.close()
                    break
                self.client_socket.send(str.encode(output))
            

    def parse_command(self, command):
        
        if not isinstance(command, list): 
            return "close"

        if command[0] == "register":
            try: 
                return self.player.register()
            except (PlayerStateViolation, PlayerTypeError) as e: 
                print("REGISTER: Remote Player proxies found a problem with error: {} in register".format(e))
                return "close"
    
        elif command[0] == "receive-stones":
            try:
                self.player.receive_stones(command[1])
                return
            except (StoneException, PlayerStateViolation, PlayerTypeError) as e:
                print("RECEIVE: Remote Player proxies found a problem with error: {} in receive".format(e))
                return "close"
          
        elif command[0] == "make-a-move":
            print("inside make a move")
            try:
                if not self.player or self.player.get_stone() == "":
                    return CRAZY_GO
                if not checkhistory(command[1], self.player.get_stone()): 
                    return ILLEGAL_HISTORY_MESSAGE
                return self.player.make_move(command[1])   
            except (StoneException, BoardException, IndexError, PlayerStateViolation, PlayerTypeError) as e:
                print("MAKE MOVE: Remote Player proxies found a problem with error: {} in make move".format(e))
                return "close"

        elif command[0] == "end-game":
            try:
                return self.player.end_game()
            except (PlayerTypeError, PlayerStateViolation) as e:
                print("END GAME: Remote Player proxies found a problem with error: {}".format(e))
                return "close"

if __name__ == "__main__":
    RemoteReferee()
