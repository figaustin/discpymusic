

class DiscPyMusicError(Exception):
    """Common base class for all exceptions that have to do with DiscPyMusic library"""
    def __init__(self, message=None) -> None:
        super().__init__(message=message)