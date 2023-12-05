from enum import Enum


class IDType(Enum):
    AUTO = 0,
    BASIC = 1,
    STRUCT = 2,
    REFERENCE = 3,
    FUNCTION = 4,
    ARRAY = 5


class BasicType(Enum):
    VOID = 0
    BOOL = 1
    INT = 2
    FLOAT = 3
    DOUBLE = 4
    STRING = 5


class UnaryOp(Enum):
    PLUS = 0
    MINUS = 1
    NOT = 2
    LOGICNOT = 3


class BinaryOp(Enum):
    PLUS = 0
    MINUS = 1
    MUL = 2
    DIV = 3
    MOD = 4
    LSHIFT = 5
    RSHIFT = 6
    AND = 7
    OR = 8
    XOR = 9
    LOGICAND = 10
    LOGICOR = 11
    EQ = 12
    NEQ = 13
    LSS = 14
    LEQ = 15
    GRE = 16
    GEQ = 17


class IOType(Enum):
    IN = 0
    OUT = 1
