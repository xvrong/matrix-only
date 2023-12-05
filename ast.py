from __future__ import annotations
from typing import List, Optional
from enums import BasicType, BinaryOp, UnaryOp, IOType


class Indent(object):
    def __init__(self, ind: int = 0) -> None:
        super().__init__()
        self.ind = ind

    def __str__(self) -> str:
        return ' ' * self.ind

    def __add__(self, i: int) -> Indent:
        return Indent(self.ind + i)


class Node(object):
    def __init__(self, row) -> None:
        super().__init__()
        self.row = row

    def __str__(self, ind=Indent()) -> str:
        return ind.__str__()

    def accept(self, visitor) -> None:
        visitor.visit(self)


class CompUnit(Node):
    def __init__(self, row) -> None:
        super().__init__(row)
        self.allDeclarationList: List[Declaration] = []
        self.blockDeclList: List[BlockDecl] = []
        self.templateDeclList: List[TemplateDecl] = []
        self.templateBlockDeclList: List[TemplateDecl] = []
        self.templateFuncDefList: List[TemplateDecl] = []
        self.funcDefList: List[FuncDef] = []

    def add_declaration(self, decl):
        if isinstance(decl, BlockDecl):
            self.blockDeclList.insert(0, decl)
        elif isinstance(decl, TemplateDecl):
            self.templateDeclList.insert(0, decl)
            if isinstance(decl.declaration, BlockDecl):
                self.templateBlockDeclList.insert(0, decl)
            elif isinstance(decl.declaration, FuncDef):
                self.templateFuncDefList.insert(0, decl)
            else:
                raise TypeError(f'unknown declaration type {type(decl)}')
        elif isinstance(decl, FuncDef):
            self.funcDefList.insert(0, decl)
        else:
            raise TypeError(f'unknown declaration type {type(decl)}')
        self.allDeclarationList.insert(0, decl)

    def __str__(self, ind=Indent()) -> str:
        out = 'CompUnit:\n'
        for decl in self.blockDeclList:
            out += decl.__str__(ind+1)
        for decl in self.templateDeclList:
            out += decl.__str__(ind+1)
        for defi in self.funcDefList:
            out += defi.__str__(ind+1)
        return out


class Declaration(Node):
    pass


class BlockDecl(Declaration):
    pass


class TypeDefDecl(BlockDecl):
    def __init__(self, row, ident, typeSpec: TypeSpecifier):
        super().__init__(row)
        self.ident = ident
        self.typeSpec = typeSpec

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}Typedef:\n{ind+1}ID: {self.ident}\n{ind+1}Type: {self.typeSpec.__str__(ind+2)}\n'


class VarDecl(BlockDecl):
    def __init__(self, row, typeSpec: Optional[TypeSpecifier], varDefList: List[VarDef], isConst: bool):
        super().__init__(row)
        self.typeSpec = typeSpec
        self.varDefList = varDefList
        for vardef in self.varDefList:
            vardef.typeSpec = self.typeSpec
        if isConst:
            for vardef in self.varDefList:
                vardef.isConst = True

    def __str__(self, ind=Indent()) -> str:
        out = f'{ind}VarDecl:\n'
        for vardef in self.varDefList:
            out += vardef.__str__(ind+1)
        return out


class VarDef(Node):
    def __init__(self, row, ident: str, initVal: Expression):
        super().__init__(row)
        self.ident = ident
        self.typeSpec = None
        self.initVal = initVal
        self.isConst = False

    def __str__(self, ind=Indent()) -> str:
        const = '(const)' if self.isConst else ''
        return f'{ind}VarDef: {const}\n{ind+1}ID: {self.ident}\n{ind+1}Type: {self.typeSpec.__str__(ind+2) if self.typeSpec else "(empty)"}\n{ind+1}Initializer:\n{self.initVal.__str__(ind+2)}'


class TemplateDecl(Declaration):
    def __init__(self, row, typeNameList: List[str], declaration: Declaration):
        super().__init__(row)
        self.typeNameList = typeNameList
        self.declaration = declaration

    def __str__(self, ind=Indent()):
        return f'{ind}Template: {self.declaration.__str__(ind+1)}'


class FuncDecl(BlockDecl):
    def __init__(self, row, ident: str, funcType: FuncType):
        super().__init__(row)
        self.ident = ident
        self.funcType = funcType

    def __str__(self, ind=Indent()) -> str:
        out = f'{ind}FuncDecl:\n'
        out += f'{ind+1}ID: {self.ident}\n'
        out += f'{self.funcType.__str__(ind+1)}'
        return out


class FuncDef(Declaration):
    def __init__(self, row, funcDecl: FuncDecl, blockStmt: BlockStmt):
        super().__init__(row)
        self.funcDecl = funcDecl
        self.blockStmt = blockStmt

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}Function Definition:\n{self.funcDecl.__str__(ind+1)}{self.blockStmt.__str__(ind+1)}'


class TypeSpecifier(Node):
    pass


class BType(TypeSpecifier):
    def __init__(self, row, bType: BasicType):
        super().__init__(row)
        self.bType = bType

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}{self.bType.name}'


class DefinedType(TypeSpecifier):
    def __init__(self, row, typeName: str):
        super().__init__(row)
        self.typeName = typeName

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}Defined type({self.typeName})'


class GenericType(TypeSpecifier):
    def __init__(self, row, typeName: str):
        super().__init__(row)
        self.typeName = typeName

    def __str__(self, ind=Indent()) -> str:
        return f'Generic Type({self.typeName})'


class ArrayType(TypeSpecifier):
    def __init__(self, row, typeSpec: TypeSpecifier, size: Optional[int]):
        super().__init__(row)
        self.typeSpec = typeSpec
        self.size = size

    def __str__(self, ind=Indent()) -> str:
        return f'{self.typeSpec.__str__(ind+1)}[{self.size or ""}]'


class StructType(TypeSpecifier):
    def __init__(self, row, ident: str, typeSpecList: List[TypeSpecifier]):
        super().__init__(row)
        self.ident = ident
        self.typeSpecList = typeSpecList

    def __str__(self, ind=Indent()) -> str:
        if len(self.typeSpecList) > 0:
            tmpstr = '<'
            for i, typeSpec in enumerate(self.typeSpecList):
                if i != 0:
                    tmpstr += ', '
                tmpstr += f'{typeSpec.__str__(ind + 1)}'
            tmpstr += '>'
        else:
            tmpstr = ''
        return f'struct {tmpstr} ({self.ident})\n'


class FuncType(TypeSpecifier):
    def __init__(self, row, funcParamList: List[FuncParam], funcRetType: Optional[TypeSpecifier] = None):
        super().__init__(row)
        self.funcParamList = funcParamList
        self.funcRetType = funcRetType

    def __str__(self, ind=Indent()) -> str:
        out = f'{ind}Function Type:\n'
        out += f'{ind+1}FuncParams:\n'
        for param in self.funcParamList:
            out += param.__str__(ind+2)
        out += f'{ind+1}FuncRetType: {self.funcRetType.__str__(ind+2) if self.funcRetType else "(Empty)"}\n'
        return out


class FuncParam(Node):
    def __init__(self, row, ident: str, paramType: Optional[TypeSpecifier] = None):
        super().__init__(row)
        self.ident = ident
        self.paramType = paramType

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}FuncParam:\n{ind+1}ID: {self.ident}\n{ind+1}Type: {self.paramType.__str__(ind+2) if self.paramType else "(Empty)"}\n'


class StructDecl(BlockDecl):
    def __init__(self, row, ident: str, memberList: List[StructMember]):
        super().__init__(row)
        self.ident = ident
        self.memberDeclList: List[MemberDecl] = []
        self.consFuncDefList: List[ConsFuncDef] = []
        self.memberFuncDefList : List[MemberFuncDef] = []

        for member in memberList:
            self.add_member(member)

    def add_member(self, member):
        if isinstance(member, MemberDecl):
            self.memberDeclList.append(member)
        elif isinstance(member, ConsFuncDef):
            self.consFuncDefList.append(member)
        elif isinstance(member, MemberFuncDef):
            self.memberFuncDefList.append(member)
        else:
            raise TypeError(f'unknown member type {type(member)}')

    def __str__(self, ind=Indent()) -> str:
        out = f'{ind}Struct Declaration:\n{ind+1}ID: {self.ident}\n'
        out += f'{ind+1}Members:\n'
        for member in self.memberDeclList:
            out += member.__str__(ind+2)
        for member in self.consFuncDefList:
            out += member.__str__(ind+2)
        for member in self.memberFuncDefList:
            out += member.__str__(ind+2)
        return out


class StructMember(Node):
    pass


class MemberDecl(StructMember):
    def __init__(self, row, ident: str, typeSpec: TypeSpecifier):
        super().__init__(row)
        self.ident = ident
        self.typeSpec = typeSpec

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}MemberDecl:\n{ind+1}ID: {self.ident}\n{ind+1}Type: {self.typeSpec.__str__(ind+2)}\n'


class ConsFuncDef(StructMember):
    def __init__(self, row, structType: StructType, funcType: FuncType, blockStmt: BlockStmt):
        super().__init__(row)
        self.structType = structType
        self.funcType = funcType
        self.blockStmt = blockStmt

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}ConsFuncDef:\n{self.structType.__str__(ind + 1)}{self.funcType.__str__(ind + 1)}{self.blockStmt.__str__(ind + 1)}'


class MemberFuncDef(StructMember):
    def __init__(self, row, funcDef: FuncDef):
        super().__init__(row)
        self.funcDef = funcDef

    def __str__(self, ind=Indent()) -> str:
        return f'{ind}MemberFuncDef:\n{self.funcDef.__str__(ind+1)}'
