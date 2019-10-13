from typing import *

def compare(object1: Any, object2: Any) -> int:
    if type(object1) is dict and type(object2) is dict:
        return compare(object1["name"], object2["name"])
    elif type(object1) is dict:
        return 1
    elif type(object2) is dict:
        return -1
    elif type(object1) is str and type(object2) is str:
        if object1 >= object2:
            return 1
        else:
            return -1
    elif type(object1) is str:
        return 1
    elif type(object2) is str:
        return -1
    else:
        if object1 >= object2:
            return 1
        else:
            return -1