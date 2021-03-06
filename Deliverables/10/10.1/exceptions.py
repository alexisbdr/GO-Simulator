class Error(Exception):
    pass 

class BoardException(Error):
    def __init__(self, message=None):
        self.msg = message

class BoardPointException(Error):
    def __init__(self, message=None):
        self.msg = message

class MaybestoneException(Error):
    def __init__(self, message=None):
        self.msg = message

class StoneException(Error):
    def __init__(self, message=None):
        self.msg = message

class PlayerException(Error):
    def __init__(self, message=None):
        self.msg = message

class PlayerStateViolation(Error):
    def __init__(self, message=None):
        self.msg = message

class PlayerTypeError(Error):
    def __init__(self, message=None):
        self.msg = message

class TournamentException(Error):
    def __init__(self, message=None):
        self.msg = message