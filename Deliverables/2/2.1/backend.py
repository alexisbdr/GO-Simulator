import sys
import json
from typing import List, Any
from json import JSONDecodeError
from functools import cmp_to_key
from utilities import compare

class backend:
    def sort(self, list_of_10: List) -> List:
        # custom sort method uses a key to sort elements
        list_of_10.sort(key = cmp_to_key(compare))
        return list_of_10