# Software Construction (CS393) Fall 2019


## GO Tournament simulator
The game of GO is a board game played between two opponents on a 19x19 grid. The code in this repository achieves the following high-level list: 
* Allows two players to play the game of GO
* Players can be in the following modes:
  * Game AI (both simple and complex strategies)
  * Network player (socket)
  * Local player (on the host computer)
* The simulator is started by the game [administrator](./Deliverables/10/10.1/administrator.py)
* Games are administered by a referee that enforces the [rules of GO](https://en.wikipedia.org/wiki/Rules_of_Go): 
  * Checks player turns are valid - valid position and no repetition
  * Removes any stones from the board that have no liberties
* Manages tournaments between multiple players in the following modes: 
  * Cup (Single-Elimination)
  * League (Round-Robin)
* Provides a GUI for viewing the progress of the game - implemented solely by @wellykachtel
* Implements a Monte Carlo Tree Search player - implemented solely by @alexisbdr


### Instructions for playing the game
To run a local test see 'testrun' - this will start both the game administrator and a remote network referee
Starting a tournament:
see 'run'. Argument 1 is the tournament mode "cup" or "league". Argument 2 is the number of players in the tournament.


### Software Design Patterns
Apart for building a fully functional (and extensively tested) GO Simulator the point of this class was to teach us re-usable and functional design patterns, here are a couple of my favorites mostly around players: 
* Proxy Design Pattern: 
  * Network players are handled by a proxy player that handles the socket connection and asks the network player to make moves. The game referee doesn't know which players are on the network or not
  * [Multiple Player Proxies](./Deliverables/10/10.1/player.py):
    * State Checking Proxy player
    * Type Checking Proxy player
* Abstract factory
  * Different types of players are generated from the [PlayerFactory](./10/10.1/player_factory.py)2:
    * GUI Players
    * Network Proxy player
    * MCTS Player
    * Default local player
* Strategy Pattern
  * Players are given a [PlayerStrategy](./Deliverables/10/10.1/player_strategy.py) that is randomly chosen allowing to play in many different ways

### File Structure
The up-to date and most recent code is in Deliverables/10/10.1

### CI 
CI testing is done through Travis CI - see makefile for travis build instructions


## Contributors
Kelly Wachtel

Alexis Baudron
