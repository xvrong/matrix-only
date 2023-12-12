from __future__ import annotations
from typing import List, Optional
from enums import BasicType, BinaryOp, UnaryOp, IOType


class Indent(object):
    def __init__(self, ind: int = 0) -> None:
        super().__init__()
        self.ind = ind

    def __str__(self):
        return ' ' * self.ind

    def __add__(self, i: int) -> Indent:
        return Indent(self.ind + i)


class Node(object):
    def __init__(self, row) -> None:
        super().__init__()
        self.row = row

    def __str__(self, ind=Indent()):
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

    def __str__(self, ind=Indent()):
        ret = 'CompUnit:\n'
        for decl in self.blockDeclList:
            ret += decl.__str__(ind+1)
        for decl in self.templateDeclList:
            ret += decl.__str__(ind+1)
        for defi in self.funcDefList:
            ret += defi.__str__(ind+1)
        return ret


class Declaration(Node):
    pass


class BlockDecl(Declaration):
    pass


class TypeDefDecl(BlockDecl):
    def __init__(self, row, ident, typeSpec: TypeSpecifier):
        super().__init__(row)
        self.ident = ident
        self.typeSpec = typeSpec

    def __str__(self, ind=Indent()):
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

    def __str__(self, ind=Indent()):
        ret = f'{ind}VarDecl:\n'
        for vardef in self.varDefList:
            ret += vardef.__str__(ind+1)
        return ret


class VarDef(Node):
    def __init__(self, row, ident: str, initVal: Expression):
        super().__init__(row)
        self.ident = ident
        self.typeSpec = None
        self.initVal = initVal
        self.isConst = False

    def __str__(self, ind=Indent()):
        const = '(const)' if self.isConst else ''
        return f'{ind}VarDef: {const}\n{ind+1}ID: {self.ident}\n{ind+1}Type: {self.typeSpec.__str__(ind+2) if self.typeSpec else "(empty)"}\n{ind+1}Initializer:\n{self.initVal.__str__(ind+2)}'


class FuncDecl(BlockDecl):
    def __init__(self, row, ident: str, funcType: FuncType):
        super().__init__(row)
        self.ident = ident
        self.funcType = funcType

    def __str__(self, ind=Indent()):
        ret = f'{ind}FuncDecl:\n'
        ret += f'{ind+1}ID: {self.ident}\n'
        ret += f'{self.funcType.__str__(ind+1)}'
        return ret


class TemplateDecl(Declaration):
    def __init__(self, row, typeNameList: List[str], declaration: Declaration):
        super().__init__(row)
        self.typeNameList = typeNameList
        self.declaration = declaration

    def __str__(self, ind=Indent()):
        return f'{ind}Template: {self.declaration.__str__(ind+1)}'


class FuncDef(Declaration):
    def __init__(self, row, funcDecl: FuncDecl, blockStmt: BlockStmt):
        super().__init__(row)
        self.funcDecl = funcDecl
        self.blockStmt = blockStmt

    def __str__(self, ind=Indent()):
        return f'{ind}Function Definition:\n{self.funcDecl.__str__(ind+1)}{self.blockStmt.__str__(ind+1)}'


class TypeSpecifier(Node):
    pass


class BType(TypeSpecifier):
    def __init__(self, row, bType: BasicType):
        super().__init__(row)
        self.bType = bType

    def __str__(self, ind=Indent()):
        return f'{ind}{self.bType.name}'


class DefinedType(TypeSpecifier):
    def __init__(self, row, typeName: str):
        super().__init__(row)
        self.typeName = typeName

    def __str__(self, ind=Indent()):
        return f'{ind}Defined type({self.typeName})'


class GenericType(TypeSpecifier):
    def __init__(self, row, typeName: str):
        super().__init__(row)
        self.typeName = typeName

    def __str__(self, ind=Indent()):
        return f'Generic Type({self.typeName})'


class ArrayType(TypeSpecifier):
    def __init__(self, row, typeSpec: TypeSpecifier, size: Optional[int]):
        super().__init__(row)
        self.typeSpec = typeSpec
        self.size = size

    def __str__(self, ind=Indent()):
        return f'{self.typeSpec.__str__(ind+1)}[{self.size or ""}]'


class StructType(TypeSpecifier):
    def __init__(self, row, ident: str, genericSpecList: List[TypeSpecifier]):
        super().__init__(row)
        self.ident = ident
        self.genericSpecList = genericSpecList

    def __str__(self, ind=Indent()):
        if len(self.genericSpecList) > 0:
            tmpstr = '<'
            for i, genericSpec in enumerate(self.genericSpecList):
                if i != 0:
                    tmpstr += ', '
                tmpstr += f'{genericSpec.__str__(ind + 1)}'
            tmpstr += '>'
        else:
            tmpstr = ''
        return f'struct {tmpstr} ({self.ident})'


class FuncType(TypeSpecifier):
    def __init__(self, row, funcParamList: List[FuncParam], funcRetType: Optional[TypeSpecifier] = None):
        super().__init__(row)
        self.funcParamList = funcParamList
        self.funcRetType = funcRetType

    def __str__(self, ind=Indent()):
        ret = f'{ind}Function Type:\n'
        ret += f'{ind+1}FuncParams:\n'
        for param in self.funcParamList:
            ret += param.__str__(ind+2)
        ret += f'{ind+1}FuncRetType: {self.funcRetType.__str__(ind+2) if self.funcRetType else "(Empty)"}\n'
        return ret


class FuncParam(Node):
    def __init__(self, row, ident: str, paramType: Optional[TypeSpecifier] = None):
        super().__init__(row)
        self.ident = ident
        self.paramType = paramType

    def __str__(self, ind=Indent()):
        return f'{ind}FuncParam:\n{ind+1}ID: {self.ident}\n{ind+1}Type: {self.paramType.__str__(ind+2) if self.paramType else "(Empty)"}\n'


class StructDecl(BlockDecl):
    def __init__(self, row, ident: str, memberList: List[StructMember]):
        super().__init__(row)
        self.ident = ident
        self.memberDeclList: List[MemberDecl] = []
        self.consFuncDefList: List[ConsFuncDef] = []
        self.memberFuncDefList: List[MemberFuncDef] = []

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

    def __str__(self, ind=Indent()):
        ret = f'{ind}Struct Declaration:\n{ind+1}ID: {self.ident}\n'
        ret += f'{ind+1}Members:\n'
        for member in self.memberDeclList:
            ret += member.__str__(ind+2)
        for member in self.consFuncDefList:
            ret += member.__str__(ind+2)
        for member in self.memberFuncDefList:
            ret += member.__str__(ind+2)
        return ret


class StructMember(Node):
    pass


class MemberDecl(StructMember):
    def __init__(self, row, ident: str, typeSpec: TypeSpecifier):
        super().__init__(row)
        self.ident = ident
        self.typeSpec = typeSpec

    def __str__(self, ind=Indent()):
        ret = f'{ind}MemberDecl:\n'
        ret += f'{ind+1}ID: {self.ident}\n'
        ret += f'{ind+1}Type: {self.typeSpec.__str__(ind+2)}\n'
        return ret


class ConsFuncDef(StructMember):
    def __init__(self, row, structType: StructType, funcType: FuncType, blockStmt: BlockStmt):
        super().__init__(row)
        self.structType = structType
        self.funcType = funcType
        self.blockStmt = blockStmt

    def __str__(self, ind=Indent()):
        ret = f'{ind}ConsFuncDef:\n'
        ret += f'{ind+1}{self.structType.__str__(ind+1)}\n'
        ret += f'{self.funcType.__str__(ind+1)}\n'
        ret += f'{self.blockStmt.__str__(ind+1)}\n'
        return ret


class MemberFuncDef(StructMember):
    def __init__(self, row, funcDef: FuncDef):
        super().__init__(row)
        self.funcDef = funcDef

    def __str__(self, ind=Indent()):
        return f'{ind}MemberFuncDef:\n{self.funcDef.__str__(ind+1)}'


class Stmt(Node):
    pass


class BlockStmt(Stmt):
    def __init__(self, row, stmtList: List[Stmt]):
        super().__init__(row)
        self.stmtList = stmtList

    def __str__(self, ind=Indent()):
        ret = f'{ind}BlockStmt:\n'
        for stmt in self.stmtList:
            ret += stmt.__str__(ind+1)
        return ret


class DeclStmt(Stmt):
    def __init__(self, row, varDecl: VarDecl):
        super().__init__(row)
        self.varDecl = varDecl

    def __str__(self, ind=Indent()):
        return f'{ind}DeclStmt:\n{self.varDecl.__str__(ind+1)}'


class AssignStmt(Stmt):
    def __init__(self, row, LVal: Expression, exp: Expression):
        super().__init__(row)
        self.LVal = LVal
        self.exp = exp

    def __str__(self, ind=Indent()):
        ret = f'{ind}AssignStmt:\n{self.LVal.__str__(ind+1)} equals {self.exp.__str__(ind+1)}'
        return ret


class ExpStmt(Stmt):
    def __init__(self, row, exp: Optional[Expression]):
        super().__init__(row)
        self.exp = exp

    def __str__(self, ind=Indent()):
        return f'{ind}Expression Statement:\n{self.exp.__str__(ind+1) if self.exp else ""}'


class IfStmt(Stmt):
    def __init__(self, row, cond: Expression, trueStmt: Stmt, falseStmt: Optional[Stmt]):
        super().__init__(row)
        self.cond = cond
        self.trueStmt = trueStmt
        self.falseStmt = falseStmt

    def __str__(self, ind=Indent()):
        ret = f'{ind}IfStmt:\n'
        ret += f'{ind+1}cond:\n{self.cond.__str__(ind+2)}'
        ret += f'{ind+1}trueStmt:\n{self.trueStmt.__str__(ind+2)}'
        ret += f'{ind+1}falseStmt:\n{self.falseStmt.__str__(ind+2) if self.falseStmt else ""}'
        return ret


class WhileStmt(Stmt):
    def __init__(self, row, cond: Expression, loopStmt: Stmt):
        super().__init__(row)
        self.cond = cond
        self.loopStmt = loopStmt

    def __str__(self, ind=Indent()):
        ret = f'{ind}WhileStmt:\n'
        ret += f'{ind+1}cond:\n{self.cond.__str__(ind+2)}'
        ret += f'{ind+1}loopStmt:\n{self.loopStmt.__str__(ind+2)}'
        return ret


class ForStmt(Stmt):
    def __init__(self, row, init: Stmt, cond: Expression, after: Stmt, loopStmt: Stmt):
        super().__init__(row)
        self.init = init
        self.cond = cond
        self.after = after
        self.loopStmt = loopStmt

    def __str__(self, ind=Indent()):
        ret = f'{ind}ForStmt:\n'
        ret += f'{ind + 1}init:\n{self.init.__str__(ind + 2)}'
        ret += f'{ind + 1}cond:\n{self.cond.__str__(ind + 2)}'
        ret += f'{ind + 1}after:\n{self.after.__str__(ind + 2)}'
        ret += f'{ind + 1}loopStmt:\n{self.loopStmt.__str__(ind + 2)}'
        return ret


class BreakStmt(Stmt):
    def __init__(self, row):
        super().__init__(row)

    def __str__(self, ind=Indent()):
        ret = f'{ind}BreakStmt\n'
        return ret


class ContinueStmt(Stmt):
    def __init__(self, row):
        super().__init__(row)

    def __str__(self, ind=Indent()):
        ret = f'{ind}ContinueStmt\n'
        return ret


class ReturnStmt(Stmt):
    def __init__(self, row, exp: Optional[Expression]):
        super().__init__(row)
        self.exp = exp

    def __str__(self, ind=Indent()):
        ret = f'{ind}ReturnStmt:\n'
        ret += f'{self.exp.__str__(ind+1) if self.exp else ""}'
        return ret


class Expression(Node):
    pass


class UnaryExp(Expression):
    def __init__(self, row, unaryOp: UnaryOp, exp: Expression):
        super().__init__(row)
        self.unaryOp = unaryOp
        self.exp = exp

    def __str__(self, ind=Indent()):
        ret = f'{ind}UnaryExp:\n'
        ret += f'{ind+1}unaryOp:{self.unaryOp.name}\n'
        ret += f'{self.exp.__str__(ind+1)}'
        return ret


class BinaryExp(Expression):
    def __init__(self, row, leftExp: Expression, binaryOp: BinaryOp, rightExp: Expression):
        super().__init__(row)
        self.leftExp = leftExp
        self.binaryOp = binaryOp
        self.rightExp = rightExp

    def __str__(self, ind=Indent()):
        ret = f'{ind}BinaryExp:\n'
        ret += f'{self.leftExp.__str__(ind+1)}'
        ret += f'{ind+1}binaryOp: {self.binaryOp.name}\n'
        ret += f'{self.rightExp.__str__(ind+1)}'
        return ret


class PostfixExp(Expression):
    pass


class PrimaryExp(PostfixExp):
    pass


class LiteralPrE(PrimaryExp):
    def __init__(self, row, literal):
        super().__init__(row)
        self.literal = literal
        
    def __str__(self, ind=Indent()):
        return f'{ind}LiteralPrE: ({self.literal.type}) {self.literal.value}\n'


class IdentPrE(PrimaryExp):
    def __init__(self, row, ident: str):
        super().__init__(row)
        self.ident = ident

    def __str__(self, ind=Indent()):
        return f'{ind}IdentPrE: {self.ident}\n'


class ExpPrE(PrimaryExp):
    def __init__(self, row, exp: Expression):
        super().__init__(row)
        self.exp = exp

    def __str__(self, ind=Indent()):
        return self.exp.__str__(ind)


class ArrayIndexExp(PostfixExp):
    def __init__(self, row, arrayExp: PostfixExp, indexExp: Expression):
        super().__init__(row)
        self.arrayExp = arrayExp
        self.indexExp = indexExp

    def __str__(self, ind=Indent()):
        ret = f'{ind}ArrayIndexExp:\n'
        ret += f'{ind+1}arrayExp:\n{self.arrayExp.__str__(ind+2)}\n'
        ret += f'{ind+1}indexExp:\n{self.indexExp.__str__(ind+2)}\n'
        return ret


class MemberExp(PostfixExp):
    def __init__(self, row, objectExp: PostfixExp, MemberID: str):
        super().__init__(row)
        self.objectExp = objectExp
        self.MemberID = MemberID

    def __str__(self, ind=Indent()):
        ret = f'{ind}MemberExp:\n'
        ret += f'{ind+1}objectExp:\n{self.objectExp.__str__(ind+2)}\n'
        ret += f'{ind+1}MemberID:\n{self.MemberID}\n'
        return ret


class ReferExp(PostfixExp):
    def __init__(self, row, referObjectExp: PostfixExp):
        super().__init__(row)
        self.referObjectExp = referObjectExp

    def __str__(self, ind=Indent()):
        ret = f'{ind}ReferExp:\n'
        ret += f'{ind+1}referObjectExp:\n{self.referObjectExp.__str__(ind+2)}\n'
        return ret


class FuncCallExp(PostfixExp):
    def __init__(self, row, funcExp: PostfixExp, genericSpecList: List[TypeSpecifier], paramExpList: List[Expression]):
        super().__init__(row)
        self.funcExp = funcExp
        self.genericSpecList = genericSpecList
        self.paramExpList = paramExpList

    def __str__(self, ind=Indent()):
        ret = f'{ind}FuncCallExp:\n'
        ret += f'{ind+1}funcExp:\n{self.funcExp.__str__(ind+2)}'
        ret += f'{ind+1}genericSpecList:\n'
        for i, genericsSpec in enumerate(self.genericSpecList):
            ret += f'{ind+2}<{i}>: {genericsSpec.__str__(ind+3)}\n'
        ret += f'{ind+1}paramExpList:\n'
        for param in self.paramExpList:
            ret += param.__str__(ind+2)
        return ret


class IOExp(PostfixExp):
    def __init__(self, row, ident: str, ioType: IOType, typeSpec: TypeSpecifier):
        super().__init__(row)
        self.ident = ident
        self.ioType = ioType
        self.typeSpec = typeSpec

    def __str__(self, ind=Indent()):
        ret = f'{ind}IOExp:\n'
        ret += f'{ind+1}ident: {self.ident}\n'
        ret += f'{ind+1}ioType: {self.ioType.name}\n'
        ret += f'{ind+1}type: {self.typeSpec.__str__(ind+2)}\n'
        return ret


class LambdaExp(PostfixExp):
    def __init__(self, row, funcType: FuncType, blockStmt: BlockStmt):
        super().__init__(row)
        self.funcType = funcType
        self.blockStmt = blockStmt

    def __str__(self, ind=Indent()):
        ret = f'{ind}Lambda Expression:\n'
        ret += f'{self.funcType.__str__(ind+1)}'
        ret += f'{self.blockStmt.__str__(ind+1)}'
        return ret
