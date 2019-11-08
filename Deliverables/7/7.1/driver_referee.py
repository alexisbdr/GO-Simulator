import socket
import sys
from utilities import readJSON
from typing import List

from definitions import *
from proxy_player import ProxyPlayer

class DriverReferee:
    
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
    
    def create_server_conn(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host , self.port))
        self.server_socket.listen(1)
        self.started = False
        self.conn, self.addr = self.server_socket.accept()
        #print("Connected to client at ", addr)

    def parse_command(self, commands: List) -> List:
        #figure out what to call on proxy and call it
        #Let's change this to a factory ---- $$$$
        outputs = []
        while True:
            try:  
                command = commands.pop(0)
            except IndexError:
                break
            if command[0] == "register":
                self.player = ProxyPlayer(self.conn, self.addr)
                output = self.player.get_name()
        
            elif command[0] == "receive-stones":
                self.player.set_color(command)
                return None

            elif command[0] == "make-a-move":
                output = self.player.make_move(command)
            else:
                raise Exception("Invalid command with statement" + command[0])
            
            output = output.decode('UTF-8')
            if output.strip() == CRAZY_GO:
                self.conn.close()
                break
            elif output: 
                outputs.append(output)
        
        return outputs
        
