BOARD_COLUMNS_MAX = 9
BOARD_COLUMNS_MIN = 1
BOARD_ROWS_MAX = 9
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
PASS_OUTPUT = "pass"

PLACE_ERROR_MESSAGE = "This seat is taken!"
REMOVE_ERROR_MESSAGE = "I am just a Board! I cannot remove what is not there!"
ILLEGAL_HISTORY_MESSAGE = "This history makes no sense!"

#Config files
GO_CONFIG_PATH = "go.config"
PLAYER_CONFIG_PATH = "go-player.config"

CRAZY_GO = "GO has gone crazy!"

N = 1

DEFAULT_PLAYER_CLASS = "DefaultPlayer"

CHEATING_PLAYER = "cheat"
