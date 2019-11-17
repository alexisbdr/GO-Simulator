import sys
import json
from json import JSONDecodeError
from rulechecker import *

from driver_referee import DriverReferee
from utilities import readJSON


class frontend: 
    def __init__(self):
        self.list_of_commands = []
        self.list_of_outputs = []
        #self.list_of_commands = readJSON(sys.stdin.read())
        self.executeCommands()
        self.printJson()

    def executeCommands(self):
        driver_referee = DriverReferee()
        self.list_of_outputs = driver_referee.parse_command()
                
    def printJson(self):
        print(json.dumps([out for out in self.list_of_outputs]))
        
if __name__ == "__main__":
    frontend()
