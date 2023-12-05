class ParseError(RuntimeError):
    def __init__(self, msg) -> None:
        super().__init__(msg)
        

class SemanticError(RuntimeError):
    def __init__(self, msg) -> None:
        super().__init__(msg)
