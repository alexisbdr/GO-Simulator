import sys
import json
from json import JSONDecodeError

sys.path.append("../2.1")
from backend import backend

class frontend:
    def __init__(self):
        self.backend = backend()
        self.list_of_objects = []
        self.lol_of_ten = []
        self.lol_sorted = []
        self.readJson()
        self.divideJson()
        self.printJson()

    def readJson(self):
        current_json = ""
        decoder = json.JSONDecoder()
        while True:
            data = sys.stdin.readline()
            if not data:
                break
            current_json = current_json + data.rstrip('\n').lstrip()
            try:
                posn = 0
                while posn < len(current_json):
                    txt, posn = decoder.raw_decode(current_json)
                    self.list_of_objects.append(txt)
                    current_json = current_json[posn:].lstrip()
                    posn = 0
            except JSONDecodeError:
                continue

    def divideJson(self):
        for i in self.list_of_objects:
            self.lol_of_ten.append(i)
            if len(self.lol_of_ten) == 10:
                self.sendReceiveList()
                self.lol_of_ten = []

    def printJson(self):
        print(json.dumps(self.lol_sorted, separators=(',', ':')))

    def sendReceiveList(self):
        sorted_list = self.backend.sort(self.lol_of_ten)
        self.lol_sorted.append(sorted_list)

if __name__ == "__main__":
    frontend()