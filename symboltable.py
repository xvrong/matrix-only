from __future__ import annotations
import copy
from typing import Dict, Optional
from type import Type


class Symbol(object):
    def __init__(self, name: str, type: Type, value: Optional[int]) -> None:
        self.name = name
        self.type = type
        self.value = value


class SymbolTable(object):
    """符号表，需要记录其父符号表的引用和域类型（函数或结构体）"""
    def __init__(self, parentSymtab: Optional[SymbolTable], parentType: Optional[Type]) -> None:
        self.parentSymtab = parentSymtab
        self.parentType = parentType
        self.typeTable: Dict[str, Type] = {}
        self.symbolTable: Dict[str, Symbol] = {}
        self.tmpIndex = 0
        self.isGlobal = self.is_global()

    def is_global(self) -> bool:
        if self.parentSymtab:
            return False
        return True

    def get_global(self) -> SymbolTable:
        if self.isGlobal:
            return self
        else:
            return self.parentSymtab.get_global()

    def add_symbol(self, name: str, type: Type, value: Optional[int] = None) -> Symbol:
        new_symbol = Symbol(name, type, value)
        self.symbolTable[name] = new_symbol
        return new_symbol

    def add_type(self, name: str, type: Type) -> str:
        self.typeTable[name] = type
        return name

    def add_tmp_type(self, type: Type) -> str:
        name = f'tmp_type_{self.tmpIndex}'
        self.add_type(name, type)
        self.tmpIndex += 1
        return name

    def get_type(self, name: str) -> Type:
        if name in self.typeTable:
            return self.typeTable[name]
        if self.parentSymtab:
            return self.parentSymtab.get_type(name)

    def get_symbol(self, name: str) -> Symbol:
        if name in self.symbolTable:
            return self.symbolTable[name]
        if self.parentSymtab:
            return self.parentSymtab.get_symbol(name)

    def get_symbol_local(self, name: str) -> Optional[Symbol]:
        if name in self.symbolTable:
            return self.symbolTable[name]
        else:
            return None

    def modify_type_local(self, name: str, type: Type) -> Type:
        if name in self.typeTable:
            self.typeTable[name] = type
            return type

    def modify_symbol_type_local(self, name: str, type: Type) -> Symbol:
        if name in self.symbolTable:
            old_symbol = self.symbolTable[name]
            self.symbolTable[name] = Symbol(old_symbol.name, type, old_symbol.value)
            return self.symbolTable[name]

    def clone(self) -> SymbolTable:
        tmp_symbol_table = SymbolTable(self.parentSymtab, self.parentType)
        tmp_symbol_table.typeTable = copy.deepcopy(self.typeTable)
        tmp_symbol_table.symbolTable = copy.deepcopy(self.symbolTable)
        tmp_symbol_table.tmpIndex = self.tmpIndex
        return tmp_symbol_table
