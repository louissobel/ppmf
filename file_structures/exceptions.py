"""
some exceptions for some exceptional incidents
"""


class FileActionImpossible(TypeError):
    """
    Attempted action not permitted
    """
    pass


class CannotWrite(FileActionImpossible):
    pass


class CannotRead(FileActionImpossible):
    pass
