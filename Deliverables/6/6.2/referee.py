import typing
from typing import List

from player import Player
from board import Board
from rulechecker import checkhistory
from definitions import *

class Referee: 

    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.pass_flag = False
        self.winner_player = None

    def start_game(self): 
        self.boards = [Board().GetBoard()]
        self.current_player = self.player1
    
    def update_boards(self, new_board):
        self.old_boards = self.boards
        self.boards = [new_board] + self.boards[:2]
    
    def switch_player(self):
        self.current_player = self.player1 if \
            self.current_player == self.player2 else self.player2
    
    def check_pass_flag(self, move: str) -> bool:
        if move == PASS_OUTPUT and self.pass_flag:
            return True
        self.pass_flag = True if move == PASS_OUTPUT else False
        return False
    
    def score_winner(self, score: dict) -> str:
        if score["B"] == score["W"]:
            return sorted([self.player1.get_name(), self.player2.get_name()])
        winner_key = max(score, key = score.get)
        self.winner_player = self.player1.get_name() if \
            winner_key == "B" else self.player2.get_name()
        return [self.winner_player]
    
    def update_state(self, Point: str):
        if self.winner_player:
            return 
        if self.check_pass_flag(Point):
            return self.score_winner(Board(self.boards[0]).count_score())
        new_board = self.current_player.make_move(Point, self.boards) 
        if new_board:
            self.update_boards(new_board)
            self.switch_player()
            return self.old_boards
        else:
            self.switch_player()
            self.winner_player = self.current_player.get_name()
            return [self.winner_player]

    def parse_command(self, command: List[str]) -> bool:
        if not self.player1: 
            self.player1 = Player(command, "B")
            self.start_game()
            return self.player1.get_stone()
        elif not self.player2: 
            self.player2 = Player(command, "W")
            return self.player2.get_stone()
        else:
            return self.update_state(command)

            



            
        
            
