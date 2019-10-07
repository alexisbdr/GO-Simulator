import sys
import json
from typing import List, Any
from json import JSONDecodeError
from functools import cmp_to_key
from utilities import compare

class backend:
    def sort(self, list_of_10: List) -> List:
        list_of_10.sort(key = cmp_to_key(compare))
        return list_of_10

    def test_driver(self):
        list_of_objects = []
        current_json = ""
        decoder = json.JSONDecoder()
        while True:
            data = sys.stdin.readline()
            if not data:
                break
            current_json = current_json + data.rstrip('\n')
            try:
                posn = 0
                while posn < len(current_json):
                    txt, posn = decoder.raw_decode(current_json)
                    list_of_objects.append(txt)
                    current_json = current_json[posn:].lstrip()
                    posn = 0
            except JSONDecodeError:
                continue
        list_of_objects = self.sort(list_of_objects)
        print(json.dumps(list_of_objects, separators=(',', ':')))