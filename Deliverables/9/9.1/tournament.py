from referee import Referee
from player_factory import PlayerFactory
from math import log2
import random
from itertools import combinations
from definitions import CHEATING_PLAYER
from exceptions import TournamentException

class Tournament:
    def __init__(self, tournament_type: str, players: list, default_path: str):
        if tournament_type == 'cup':
            self.tournament = Cup(players)
        elif tournament_type == 'league':
            self.tournament = League(players, default_path)
        else:
            raise TournamentException("Not a valid tournament type")

    def print_results(self):
        self.tournament.print_results()
    
    def get_participating_players(self):
        return self.tournament.get_participating_players()

class Cup:

    def __init__(self, players: list):
        self.players = players
        self.results = {} # {round: [player1, player2, ...]}
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
            winner, loser = 0,1
            if game[0][1] == game[1][1]:
                coin_flip = random.randint(0,1)
                winner = coin_flip
                loser = 0 if winner else 1
            next_round_players.append(game[winner][0])
            loser_player_name = game[loser][0]
            if self.round in self.results:
                self.results[self.round].append(loser_player_name)
            else: 
                self.results[self.round] = [loser_player_name]
        self.round += 1
        self.run(next_round_players)

    def print_results(self):
        print("===== Final Results =====")
        print("Winner: ", self.results["winner"][0].get_name())
        for key, val in self.results.items():
            if key == 'winner':
                continue
        
            string = ""
            for i, p in enumerate(val):
                if i == 0:
                    string += p.get_name()
                else:
                    string += ", " + p.get_name()
            print("Eliminated in round ", int(key), ": ", string)
    
    def get_participating_players(self):
        return [p for key in self.results for p in self.results[key]]
            
class League:

    def __init__(self, players: list, default_path:str):
        self.players = players
        self.default_player = default_path
        self.player_score = {} # {player: score}
        #Initialize each player score to 0
        for player in self.players: 
            self.player_score[player] = 0
        self.game_results = {} # { (player_idx1, player_idx2): winner_player_idx}
        self.run()

    def run(self):
        """
        Explanation:
            -Creates a schedule = [(player_idx0, player_idx1), (player_idx0, player_idx2), ...] 
            -Enumerates through the schedule and sends players to the referee to administer a game 
                and handles the following cases: 
                -Cheating: Creates a default player, update the scores and backtrack through existing results
                    to award player points to players eliminated by the cheating player
                -Not Cheating: Coin flip if there's a draw and update scores
        """
        print("starting league")
        self.schedule = combinations(range(len(self.players)), 2)
        for matchup in self.schedule:
            print(matchup)
            game = Referee(self.players[matchup[0]], self.players[matchup[1]]).get_results()
            print(game)
            if game[2]:
                self.handle_cheater(game, matchup)               
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
                if winning_player == self.players[matchup[0]]:
                    self.game_results[matchup] = matchup[0]
                else: self.game_results[matchup] = matchup[1]
        return

    def handle_cheater(self, game_result, current_matchup):
        """
            game_result is in the format 
            
                [[winner_player_object, score], [cheating_player_object, score], cheating_flag]
            
            current_matchup is a tuple containing the two 
            indicies of the self.players objects that are playing each other
        
        """
        # Generate the new default player that will be taking the place
        # of the cheating player for the remaining games
        new_player = PlayerFactory(path=self.default_player).create()
        new_player.register()

        cheating_player = game_result[1][0]
        winning_player = game_result[0][0]
        self.player_score[cheating_player] = -1
        self.player_score[new_player] = 0
        self.player_score[winning_player] += 1

        if cheating_player == self.players[current_matchup[0]]:
            self.players[current_matchup[0]] = new_player
            self.game_results[current_matchup] = current_matchup[1]
            cheating_player = current_matchup[0]
        else: 
            self.players[current_matchup[1]] = new_player
            self.game_results[current_matchup] = current_matchup[0]
            cheating_player = current_matchup[1]
        
        self.fix_history(cheating_player)

    def fix_history(self, cheater):
        for played_game, winner in self.game_results.items(): 
            if cheater == winner:
                loser_player = played_game[0] if winner == played_game[1] else played_game[1]
                self.game_results[played_game] = loser_player
                if self.player_score[self.players[loser_player]] != CHEATING_PLAYER:
                    self.player_score[self.players[loser_player]] += 1


    def print_results(self):
        print("===== Final Results =====")
        results = self.player_score
        results = sorted(results.items(), key=lambda kv: kv[1], reverse=True)
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
    
    def get_participating_players(self):
        return [p for p in self.player_score]        
        