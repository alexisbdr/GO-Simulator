import sys
from dataclasses import dataclass
import json
from json import JSONDecodeError

from board import Board
 
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
        for command in self.list_of_commands:
            board = command[0]
            statement = command[1]
            result = Board(board, statement)
            self.list_of_outputs.append(result)

    def printJson(self):
        print(json.dumps([str(out) for out in self.list_of_outputs]))
        