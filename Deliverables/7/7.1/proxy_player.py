import json

from player import Player

class ProxyPlayer(Player):
    
    def _init__(self):
        self.name = "no name"
        self.stone = ""

    def set_conn(self, conn):
        self.conn = conn
        
    def get_name(self, command):
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024)
    
    def get_stone(self, command):
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024)

    def set_color(self, command):
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024)

    def make_move(self, command):
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024)

    def close(self):
        self.conn.send(b"close")
        return "close"
