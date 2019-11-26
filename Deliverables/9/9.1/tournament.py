from referee import Referee
from player_factory import PlayerFactory
from math import log2
import random
from itertools import combinations
from definitions import CHEATING_PLAYER

class Cup:

    def __init__(self, players: list):
        self.players = players
        self.results = {}
        self.round = 1
        self.run(self.players)
    
    def run(self, players: list):
        print("starting cup")
        next_round_players = []
        if len(players) == 1:
            self.results['winner'] = players[0].get_name()
            return
        for p in range(0, len(players), 2):
            game = Referee(players[p], players[p+1]).get_results()
            print(game)
            winner, loser = 0,1
            if game[0][1] == game[1][1]:
                coin_flip = random.randint(0,1)
                winner = coin_flip
                loser = 0 if winner else 1
            next_round_players.append(game[winner][0])
            loser_player_name = game[loser][0].get_name()
            if self.round in self.results:
                self.results[self.round].append(loser_player_name)
            else: 
                self.results[self.round] = [loser_player_name]
        self.round += 1
        self.run(next_round_players)
    
    def get_results(self):
        return self.results
            
class League:

    def __init__(self, players: list, default_path:str):
        self.players = players
        self.default_player = default_path
        self.player_score = {}
        for player in self.players: 
            self.player_score[player] = 0
        self.game_results = {}
        self.run()

    def run(self):
        print("starting league")
        schedule = combinations(range(len(self.players)), 2)
        for index, g in enumerate(schedule):
            #print(g)
            game = Referee(self.players[g[0]], self.players[g[1]]).get_results()
            print(game)
            if game[2]:
                new_player = PlayerFactory(path=self.default_player).create()
                new_player.register()
                cheating_player = game[1][0]
                self.player_score[cheating_player] = -1
                self.player_score[new_player] = 0
                self.player_score[game[0][0]] += 1
                if cheating_player == self.players[g[0]]:
                    self.players[g[0]] = new_player
                    self.game_results[g] = g[1]
                    cheating_player = g[0]
                else: 
                    self.players[g[1]] = new_player
                    self.game_results[g] = g[0]
                    cheating_player = g[1]
                for played_game, winner in self.game_results.items(): 
                    if cheating_player == winner:
                        loser_player = played_game[0] if winner == played_game[1] else played_game[1]
                        self.game_results[played_game] = loser_player
                        if self.player_score[self.players[loser_player]] != CHEATING_PLAYER:
                            self.player_score[self.players[loser_player]] += 1
            else: 
                #Draw situation
                winner,loser = 0,1
                if game[0][1] == game[1][1]:
                    coin_flip = random.randint(0,1)
                    winner = coin_flip
                    loser = 0 if coin_flip else 1
                self.player_score[game[winner][0]] += 1
                self.player_score[game[loser][0]] += 0
                winning_player = game[winner][0]
                if winning_player == self.players[g[0]]:
                    self.game_results[g] = g[0]
                else: self.game_results[g] = g[1]
    
    def get_results(self):
        return self.player_score
        

                        

                
            



        
        