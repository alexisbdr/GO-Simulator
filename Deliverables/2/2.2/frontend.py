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

    ## reads in special JSON objects from user using stdin
    ## appends each special JSON object to a list of all objects
    def readJson(self):
        current_json = ""
        decoder = json.JSONDecoder()
        while True:
            data = sys.stdin.readline()
            if not data:
                break
            ## readline attaches /n character to each line
            current_json = current_json + data.rstrip('\n').lstrip()
            try:
                posn = 0
                while posn < len(current_json):
                    ## raw_decode finds the first special json object present in the string
                    ## returns a tuple
                    ## txt is the Python representation of the JSON (dict, int/float, Unicode string)
                    ## posn is the index at which the special json object stops
                    txt, posn = decoder.raw_decode(current_json)
                    self.list_of_objects.append(txt)
                    current_json = current_json[posn:].lstrip()
                    posn = 0
            except JSONDecodeError: ## continue on to read next line
                continue

    ## divides the complete list of special JSON objects into lists of 10
    ## saves a list of 10 special JSON objects that have not been sorted yet into lol_of_ten
    ## invokes sendReceiveList
    ## disregards leftover elements not added to a list of 10
    def divideJson(self):
        for i in self.list_of_objects:
            self.lol_of_ten.append(i)
            if len(self.lol_of_ten) == 10:
                self.sendReceiveList()
                self.lol_of_ten = []

    def printJson(self):
        ## serializes python objects into JSON, removes spacing around commas and colons
        print(json.dumps(self.lol_sorted, separators=(',', ':')))

    def sendReceiveList(self):
        # invokes backend to sort the list of ten
        sorted_list = self.backend.sort(self.lol_of_ten)
        # attends the sorted list to a list of lists of sorted items
        self.lol_sorted.append(sorted_list)

if __name__ == "__main__":
    frontend()