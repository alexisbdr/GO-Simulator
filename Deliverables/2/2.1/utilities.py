from typing import *

# recursive function to compare two objects
# return positive value to sort object1 to the right of object2
# return negative value to sort object1 to the left of object2
# return 0 if objects are equal
def compare(object1: Any, object2: Any) -> int:
    if type(object1) is dict and type(object2) is dict:
        return compare(object1["name"], object2["name"])  # we know we need to use the value of "name" to sort objects
    elif type(object1) is dict:  # object2 must not be a dict so object1 is sorted to the right of object2
        return 1
    elif type(object2) is dict:  # object1 must not be a dict so object2 is sorted to the right of object1
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