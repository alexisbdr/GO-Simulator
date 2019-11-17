import typing
from typing import List

from board import Board
from rulechecker import checkhistory, place_stone
from definitions import *
import json

class Referee: 

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.pass_flag = False
        self.winner_player = None

        self.player1.set_stone("B")
        self.player2.set_stone("W")
        
        self.start_game()
    
    def get_winner(self):
        return self.winner_player
            
    def update_boards(self, new_board):
        self.old_boards = self.boards
        self.boards = [new_board] + self.boards[:2]
    
    def switch_player(self):
        self.current_player = self.player1 if \
            self.current_player == self.player2 else self.player2
    
    def check_pass_flag(self, move: str):# -> bool:
        if move == PASS_OUTPUT and self.pass_flag:
            return True
        self.pass_flag = True if move == PASS_OUTPUT else False
        return False
    
    def score_winner(self, score: dict):# -> str:
        if score["B"] == score["W"]:
            return sorted([self.player1.get_name(), self.player2.get_name()])
        winner_key = max(score, key = score.get)
        self.winner_player = self.player1.get_name() if \
            winner_key == "B" else self.player2.get_name()
        return [self.winner_player]
    
    def update_state(self, Point: str):
        if self.check_pass_flag(Point):
            self.winner_player = self.score_winner(Board(self.boards[0]).count_score())
            return
        new_board = place_stone(self.boards[0], self.current_player.get_color(), Point) 
        print(new_board)
        if new_board:
            self.update_boards(new_board)
            self.switch_player()
        else:
            self.switch_player()
            self.winner_player = self.current_player.get_name()
        return

    def start_game(self): 
        print("Starting game")
        self.boards = [Board().get_board()]
        for row in self.boards[0]:
            print(row)
        print(self.boards[0])
        self.current_player = self.player1
        while not self.winner_player:
            point = self.current_player.make_move(self.boards)
            self.update_state(point)
        print("There is a winner")


            



            
        
            
