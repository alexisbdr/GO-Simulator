import json

from abstract_player import AbstractPlayer

class ProxyPlayer(AbstractPlayer):
    
    def _init__(self):
        self.name = ""
        self.stone = ""

    def set_conn(self, conn):
        self.conn = conn
        
    def get_name(self):
        self.conn.send(str.encode(json.dumps(["register"])))
        self.name = self.conn.recv(1024).decode("UTF-8")
        return self.name
    
    def get_stone(self):
        return self.stone

    def set_stone(self, color):
        self.stone = color
        command = ["receive-stones"]
        command.append(color)
        self.conn.send(str.encode(json.dumps(command)))
        self.conn.recv(1024).decode("UTF-8")

    def make_move(self, boards):
        command = ["make-a-move"]
        command.append(boards)
        self.conn.send(str.encode(json.dumps(command)))
        return self.conn.recv(1024).decode("UTF-8")

    def close(self):
        self.conn.send(b"close")
        return "close"
