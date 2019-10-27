BOARD_COLUMNS_MAX = 19
BOARD_COLUMNS_MIN = 1
BOARD_COLUMNS_MAX = 19
BOARD_ROWS_MAX = 19
BOARD_ROWS_MIN = 1
STONE = ["B", "W"]
EMPTY_STONE = " "
MAYBE_STONE = ["B", "W", " "]
COMMANDS = {"occupied?": 2, 
            "occupies?": 3, 
            "reachable?": 3, 
            "place": 3, 
            "remove": 3, 
            "get-points": 2}

#OUTPUTS AND MESSAGES
TRUE_OUTPUT = True
FALSE_OUTPUT = False

PLACE_ERROR_MESSAGE = "This seat is taken!"
REMOVE_ERROR_MESSAGE = "I am just a Board! I cannot remove what is not there!"
ILLEGAL_HISTORY_MESSAGE = "This history makes no sense!"

