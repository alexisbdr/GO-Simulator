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
        try:
            self.server_socket.bind((self.host , self.port))
        except OSError:
            print("Socket error. Try again")
            sys.exit()
        self.server_socket.listen(5)
        self.started = False
        #print("Listening for client . . .")
        self.conn, self.addr = self.server_socket.accept()
        #print("Connected to client at ", self.addr)

    def parse_command(self):
        #figure out what to call on proxy and call it
        #Let's change this to a factory ---- $$$$
        commands = readJSON(sys.stdin.read())
        outputs = []
        while True:
            try:  
                command = commands.pop(0)
            except IndexError:
                break

            if command[0] == "register":
                self.player = ProxyPlayer()
                self.player.set_conn(self.conn)
                output = self.player.get_name(command)
        
            elif command[0] == "receive-stones":
                output = self.player.set_color(command)

            elif command[0] == "make-a-move":
                output = self.player.make_move(command)

            else:
                output = CRAZY_GO
            
            output = output.decode('UTF-8')
            if output.strip() == CRAZY_GO:
                outputs.append(output)
                break
            elif output == 'RECEIVE':
                continue
            elif output: 
                outputs.append(output)

        self.close_connection()
        return outputs
        
    def close_connection(self):
        self.player.close()
        self.conn.close()

