from referee import Referee
from player_factory import PlayerFactory
from math import log2
import random
from itertools import combinations
from definitions import CHEATING_PLAYER_SCORE

class Cup:

    def __init__(self, players: list):
        self.players = players
        self.results = {} # {round: [player, player, ...]}
        self.round = 1
        self.run(self.players)

    def run(self, players: list):
        """
        Input: 
            players: a list of the players in the current round, always a power of 2
        Explanation: 
            -called recursively until there is only one player left. 
            -sends players two-by-two to the referee
            -updates the list of players and the result dictionary
        """
        next_round_players = []
        if len(players) == 1:
            self.results['winner'] = [players[0]]
            return
        for p in range(0, len(players), 2):
            game = Referee(players[p], players[p+1]).get_results()
            print(game)
            winner, loser = 0,1 #Winner should be at index 0, loser at index 1
            #Draw situation - perform a coin flip to determine the winner
            if game[0][1] == game[1][1]:
                coin_flip = random.randint(0,1)
                winner = coin_flip
                loser = 0 if winner else 1
            #Add the winner to the list of players for the next round
            next_round_players.append(game[winner][0])
            loser_player_name = game[loser][0]
            #Append loser name to list of players for current round
            if self.round in self.results:
                self.results[self.round].append(loser_player_name)
            else: 
                self.results[self.round] = [loser_player_name]
        self.round += 1
        self.run(next_round_players)
    
    def get_results(self):
        return self.results
    
    def print_results(self):
        print("===== Final Rankings =====")
        results = sorted(self.results.items(), key=lambda kv: kv[1], reverse=True)
        prev_val = -1
        rank = 0
        for item in results:
            key = item[0]
            val = item[1]
            if val == prev_val:
                if val == -1:
                    print(key.get_name())
                else:
                    print("   " + key.get_name(), "("+ str(val)+")")
            else:
                rank +=1
                if val == -1:
                    print("Cheater(s): ")
                    print(key.get_name())
                else:
                    print(str(rank)+". ",end='')
                    print(key.get_name(), " ("+ str(val)+")")
            prev_val = val

class League:

    def __init__(self, players: list, default_path:str):
        self.players = players
        self.default_player = default_path
        self.player_score = {} # {player: score} 
        self.game_results = {} # { (game_idx1, game_idx2): winner_game_idx }
        self.run()

    def run(self):
        """
        Explanation:
            -Creates a schedule = [(player_idx0, player_idx1), (player_idx0, player_idx2), ...] 
            -Enumerates through the schedule and sends players to the referee to administer a game 
                and handles the following cases: 
                -Cheating: Creates a new player and 
        """
        print("starting league")
        #Set all player scores to initial value: 0
        for player in self.players: 
            self.player_score[player] = 0
        #Creates a two-by-two schedule of player indices
        schedule = combinations(range(len(self.players)), 2)
        for index, g in enumerate(schedule):
            print(g)
            game = Referee(self.players[g[0]], self.players[g[1]]).get_results()
            print(game)
            #Check for cheating_flag
            if game[2]:
                #Create new player from path and register
                new_player = PlayerFactory(path=self.default_player).create()
                new_player.register()
                cheating_player = game[1][0]
                #Set the scores for each player
                self.player_score[cheating_player] = CHEATING_PLAYER_SCORE
                self.player_score[new_player] = 0
                self.player_score[game[0][0]] += 1
                #Update the players list and set the game winner in the game_results dict
                if cheating_player == self.players[g[0]]:
                    self.players[g[0]] = new_player
                    self.game_results[g] = g[1]
                    cheating_player = g[0]
                else: 
                    self.players[g[1]] = new_player
                    self.game_results[g] = g[0]
                    cheating_player = g[1]
                #Update the old games to award any points to previous opponents
                for played_game, winner in self.game_results.items():
                    # e.g: (player_idx1, player_idx2), player_idx1 
                    if cheating_player == winner:
                        #Update the game results dictionary by setting making it the non-cheater index
                        loser_player = played_game[0] if winner == played_game[1] else played_game[1]
                        self.game_results[played_game] = loser_player
                        #If that player wasn't a cheater - increase it's overall score by 1
                        if self.player_score[self.players[loser_player]] != CHEATING_PLAYER_SCORE:
                            self.player_score[self.players[loser_player]] += 1
            else: 
                #Draw situation
                winner,loser = 0,1
                if game[0][1] == game[1][1]:
                    coin_flip = random.randint(0,1)
                    winner = coin_flip
                    loser = 0 if coin_flip else 1
                #Update the player scores 
                self.player_score[game[winner][0]] += 1
                self.player_score[game[loser][0]] += 0
                winning_player = game[winner][0]
                #Update the game results
                if winning_player == self.players[g[0]]:
                    self.game_results[g] = g[0]
                else: self.game_results[g] = g[1]
        return
    
    def get_results(self):
        print(self.players)
        return self.player_score
    
    def print_results(self):
        print("===== Final Rankings =====")
        print("Winner: ", self.player_score["winner"][0].get_name())
        for key, val in self.player_score.items():
            if key == 'winner':
                continue
        
            string = ""
            for i, p in enumerate(val):
                if i == 0:
                    string += p.get_name()
                else:
                    string += ", " + p.get_name()
            print("Eliminated in round ", int(key), ": ", string)

                        

                
            



        
        