import sys
import json
from typing import List, Any
from json import JSONDecodeError
from functools import cmp_to_key
from backend import backend

## reads in special JSON objects from user using stdin
## appends each special JSON object to a list of all objects
def test_driver():
    back = backend()
    list_of_objects = []
    current_json = ""
    decoder = json.JSONDecoder()
    while True:
        data = sys.stdin.readline()
        if not data:
            break
        current_json = current_json + data.rstrip('\n').lstrip()
        number_of_objects = 0
        try:
            posn = 0
            while posn < len(current_json):
                ## raw_decode finds the first special json object present in the string
                ## returns a tuple
                ## txt is the Python representation of the JSON (dict, int/float, Unicode string)
                ## posn is the index at which the special json object stops
                txt, posn = decoder.raw_decode(current_json)
                list_of_objects.append(txt)
                number_of_objects+=1
                current_json = current_json[posn:].lstrip()
                posn = 0
                if number_of_objects == 10:
                    break
        except JSONDecodeError:  ## continue on to read next line
            continue
    list_of_objects = back.sort(list_of_objects)
    print(json.dumps(list_of_objects), separators=(",",":"))

if __name__ == "__main__":
    test_driver()
