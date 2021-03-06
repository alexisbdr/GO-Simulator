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

DEFAULT_PLAYER_CLASS = "RandomStrategyPlayer"

CHEATING_PLAYER = "cheat"


END_GAME_MESSAGE = "OK"

INVALID_TURN = 30

SQUARE_SIZE = 50

RIGHT_OFFSET = 200
TOP_OFFSET = 50
LEFT_OFFSET = 50
BOTTOM_OFFSET = 50
BOARD_HEIGHT = BOARD_ROWS_MAX * SQUARE_SIZE
BOARD_WIDTH = BOARD_COLUMNS_MAX * SQUARE_SIZE 
WINDOW_HEIGHT = BOARD_HEIGHT + TOP_OFFSET + BOTTOM_OFFSET
WINDOW_WIDTH = BOARD_WIDTH + RIGHT_OFFSET + LEFT_OFFSET

HALF_WINDOW_HEIGHT = WINDOW_HEIGHT / 2
HALF_WINDOW_WIDTH = WINDOW_WIDTH / 2

POINT_BUFFER = 10

TEXTBOX_WIDTH = 20
STONE_RADIUS = 15

