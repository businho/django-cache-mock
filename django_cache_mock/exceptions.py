class LazyLibImportError(Exception):
    parent_exception = None

    def __init__(self, server, params):
        raise self from self.parent_exception
