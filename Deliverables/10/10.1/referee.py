import typing
from typing import List

from board import Board
from rulechecker import checkhistory, place_stone
from definitions import *
import json
from exceptions import BoardPointException


class Referee: 

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.pass_flag = False
        self.winner_player = None
        self.results = []
        self.game_over = False
        self.start_game()
    
    def get_results(self):
        return self.results
            
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
    
    
    def update_state(self, Point: str):
        print(self.current_player.get_name(), Point)
        if self.check_pass_flag(Point):
            self.end_game()
            self.game_over = True
            return
        try:
            new_board = place_stone(self.boards[0], self.current_player.get_stone(), Point) 
        except BoardPointException:
            new_board = False
        if new_board:
            for row in new_board:
                print(row)
            self.update_boards(new_board)
            self.switch_player()
        else:
            print(new_board)
            self.switch_player()
            self.end_game(cheating=True)
            self.game_over = True
        return

    def start_game(self): 
        
        self.player1.receive_stones("B")
        self.player2.receive_stones("W")

        self.boards = [Board().get_board()]
        self.current_player = self.player1
        while not self.game_over:
            point = self.current_player.make_move(self.boards)
            self.update_state(point)
    
    def end_game(self, cheating=False):
        """
        Sets the results list:
        [(winner_player, score, cheating_flag), (loser_player, score, cheating_flag)]
        """
        #Update both players with the end game signal - think about the ordering in this
        resp1 = self.player1.end_game()

        if not resp1 or resp1 != "OK":
            self.results = [(self.player2, 0), (self.player1, 0), True]
            return
        
        resp2 = self.player2.end_game()
        if not resp2 or resp2 != "OK":
            self.results = [(self.player1, 0), (self.player2, 0), True]
            return

        score = Board(self.boards[0]).count_score()
        score_player1 = score["B"]
        score_player2 = score["W"]
        if not cheating:
            #Send end message to both and see if one of them disconnects
            self.results = [[self.player1, score_player1], 
                [self.player2, score_player2]]
            self.results = sorted(self.results, key=lambda x : x[1], reverse=True)
        else:
            if self.current_player == self.player1:
                self.results = [(self.current_player, score_player1), (self.player2, score_player2)]
            else:
                self.results = [(self.current_player, score_player2), (self.player1, score_player1)]
        self.results.append(cheating)
        

        




            



            
        
            
