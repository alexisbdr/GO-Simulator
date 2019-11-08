import json

from player import Player

class ProxyPlayer(Player):
    
    def _init__(self, conn , addr):
        self.conn = conn
        self.addr = addr
        self.name = "no name"
        self.stone = ""
        
    def get_name(self, command):
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024)
    
    def get_stone(self, command):
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024)

    def make_move(self, command):
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024)
