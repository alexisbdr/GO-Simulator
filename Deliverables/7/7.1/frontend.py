import sys
import json
from json import JSONDecodeError
from rulechecker import *

from referee import Referee

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8080       # The port used by the server



class frontend: 
    def __init__(self):
        self.list_of_commands = []
        self.list_of_outputs = []
        self.readJSON()
        self.executeCommands()
        self.printJson()

    def readJSON(self):
        current_json = ""
        decoder = json.JSONDecoder()
        while True:
            data = sys.stdin.readline()
            if not data:
                break
            current_json = current_json + data.rstrip('\n').lstrip()
            try:
                posn = 0
                while posn < len(current_json):
                    txt, posn = decoder.raw_decode(current_json)
                    #print(self.list_of_commands)
                    self.list_of_commands.append(txt)
                    current_json = current_json[posn:].lstrip()
                    posn = 0
            except JSONDecodeError:
                continue

    def executeCommands(self):
        referee = Referee()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            for command in self.list_of_commands:
            
                s.sendall(command)
                data = s.recv(1024)
                print('Received', repr(data))
                #Handling single board -> count score
                """output, output1 = referee.parse_command(command)
                self.list_of_outputs.append(output) if output else None
                self.list_of_outputs.append(output1) if output1 else None"""
                
    def printJson(self):
        print(json.dumps([out for out in self.list_of_outputs]))
        