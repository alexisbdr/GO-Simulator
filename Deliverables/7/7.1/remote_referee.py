import sys
import json
from json import JSONDecodeError
from rulechecker import *
from json_reader import readJSON
from referee import Referee

import socket

class Remote: 
    def __init__(self):
        self.list_of_commands = []
        self.list_of_outputs = []
        file = open('go.config', 'r')
        file = file.read()
        netData = readJSON(file)
        netData = netData[0]
        HOST = netData['IP']
        PORT = netData['port']
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

   
        data = "starting"
        print('send to server: ', data)
        client_socket.send(str.encode(data))
        server_response = client_socket.recv(131072)
        self.list_of_commands = readJSON(server_response.decode("utf-8"))
        #print(self.list_of_commands)
        self.executeCommands()
        client_socket.send(str.encode(json.dumps([out for out in self.list_of_outputs])))
        server_response = client_socket.recv(131072)

        print("disconnecting")
        client_socket.send(b"Disconnecting")
        client_socket.close()
        """with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'')
            data = s.recv(1024)
        print(data)"""
            #self.list_of_commands = readJSON(data.decode("utf-8"))
            #self.executeCommands()
            #s.sendall(json.dumps([out for out in self.list_of_outputs]))
            #self.printJson()


    def executeCommands(self):
        referee = Referee()
        for command in self.list_of_commands:
            #Handling single board -> count score
            output = referee.parse_command(command)
            self.list_of_outputs.append(output) if output else None
                
    def printJson(self):
        print(json.dumps([out for out in self.list_of_outputs]))

Remote()