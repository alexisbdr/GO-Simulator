import typing
from typing import List

from player import Player
from rulechecker import checkhistory
from definitions import *

class Game: 

    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.turn_count = 0
        self.play_depth = N

    def parse_command(self, command: List[str]) -> bool:
        self.turn_count+=1
        if command[0] == "register":
            self.player1 = Player("no name")
            return self.player1.get_name()
        
        elif command[0] == "receive-stones":
            self.player1.set_color(command[1])
            return None
        
        elif command[0] == "make-a-move":
            if not checkhistory(command[1], self.player1.get_color()): 
                return ILLEGAL_HISTORY_MESSAGE
            return self.player1.make_move_two(command[1], self.play_depth)
        else:
            raise Exception("Invalid command with statement" + command[0])
