from __future__ import annotations
from abc import ABC, abstractmethod
from random import randrange
from typing import List
from tournament import Tournament
from referee import Referee
from administrator import Administrator


class AdminObserver():
    def update(self, administrator):
        print(administrator.state)


class TournamentObserver():
    def update(self, tournament):
        print(tournament.state)

class RefereeObserver():
    def update(self, referee):
        print(referee.state)