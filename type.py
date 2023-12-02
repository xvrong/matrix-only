from __future__ import annotations
import copy
from typing import Dict, List, Optional, Tuple
from llvmlite import ir
from ast import Node
from enums import BasicType, IDType
from error import SemanticError
import symboltable
# from .utils.misc import merge_matched


class Type(object):
    def __init__(self,
                 id_type: Optional[IDType] = None,
                 basic_type: Optional[BasicType] = None,
                 generic_name: Optional[str] = None,
                 generic_type_range: Optional[Type] = None,
                 struct_name: Optional[str] = None) -> None:
        assert ((basic_type or generic_name or struct_name) and
                not (basic_type and generic_name) or
                not (basic_type and struct_name) or
                not (generic_name and struct_name))
        self.isConst = False
        self.dims: List[int] = []  # 0 for empty size

        # ID type
        self.idType: Optional[IDType] = id_type
        # Basic type
        self.basic_type: Optional[BasicType] = basic_type

        # Generic type
        self.generic_name: Optional[str] = generic_name
        self.generic_type_range: Optional[Type] = generic_type_range

        # Struct type
        self.struct_name: Optional[str] = struct_name
        self.base_type_list: List[Type] = []
        self.member_list: List[symboltable.Symbol] = []
        self.constructor: Optional[symboltable.Symbol] = None

        # Reference type
        self.reference = False

        # Function type
        self.func_ret_type: Optional[Type] = None
        self.func_params: List[symboltable.Symbol] = []

        # Struct / Interface / Function type
        self.generics_type_list: List[Type] = []
        self.symbol_table: Optional[symboltable.SymbolTable] = None
        self.unParsed: Optional[Node] = None

        if self.idType is None:
            self.idType = self.judge_idtype()

    def judge_idtype(self) -> IDType:
        if self.func_ret_type is not None:
            return IDType.FUNCTION
        elif self.reference:
            return IDType.REFERENCE
        elif self.struct_name is not None:
            return IDType.STRUCT
        elif self.generic_name is not None:
            return IDType.GENERIC
        elif self.basic_type is not None:
            return IDType.BASIC
        else:
            return IDType.AUTO

    def has_generics(self) -> bool:
        return len(self.generics_type_list) > 0

    def is_generics(self) -> bool:
        idtype = self.idType
        if idtype == IDType.AUTO:
            return False
        elif idtype == IDType.BASIC:
            return False
        elif idtype == IDType.GENERIC:
            return True
        elif idtype == IDType.STRUCT:
            for generics_type in self.generics_type_list:
                if generics_type.is_generics():
                    return True
            return False
        elif idtype == IDType.REFERENCE:
            refered_type = self.clone().remove_ref()
            return refered_type.is_generics()
        elif idtype == IDType.FUNCTION:
            for param_symbol in self.func_params:
                if param_symbol.type.is_generics():
                    return True
            return self.func_ret_type.is_generics()
        else:
            assert False

    def add_const(self) -> Type:
        self.isConst = True
        return self

    def add_symbol_table(self, parent_symbol_table: symboltable.SymbolTable) -> Type:
        self.symbol_table = symboltable.SymbolTable(parent_symbol_table, self)
        return self

    def add_generics_type(self, generics_type: Type) -> Type:
        assert generics_type.idType == IDType.GENERIC
        self.generics_type_list.append(generics_type)
        if len(generics_type.generic_name) > 0:
            self.symbol_table.add_type(generics_type.generic_name, generics_type)
        else:
            generics_type.generic_name = self.symbol_table.add_unnamed_type(generics_type)
        return self

    # def add_struct_base_type(self, base_type: Type) -> Type:
    #     self.base_type_list.append(base_type)
    #     return self

    def add_struct_member(self, member: symboltable.Symbol) -> Type:
        self.member_list.append(member)
        return self

    def add_array_dim_chosen(self, dim_index: int, dim_size: int) -> Type:
        kind = self.idType
        if kind == IDType.BASIC and self.basic_type == BasicType.VOID:
            raise SemanticError('can not create array of void')
        if kind == IDType.REFERENCE:
            raise SemanticError('type of array element can not be reference')
        self.dims.insert(dim_index, dim_size)
        return self

    def add_ref(self) -> Type:
        if self.reference:
            raise SemanticError('can not create a reference to reference type')
        self.reference = True
        return self

    def add_func_param(self, param: symboltable.Symbol) -> Type:
        self.func_params.append(param)
        return self

    def add_func_ret_type(self, ret_type: Type) -> Type:
        assert self.func_ret_type is None
        self.func_ret_type = ret_type
        return self

    def array_element(self) -> Type:
        self.dims.pop()
        return self

    def get_array_size_chosen(self, dim_index: int) -> int:
        return self.dims[dim_index]

    def get_dim_size(self) -> int:
        return len(self.dims)

    def remove_ref(self) -> Type:
        assert self.idType == IDType.REFERENCE
        self.reference = False
        return self

    def clone(self, clone_symbol_table=False) -> Type:
        tmp_type = Type(basic_type=self.basic_type,
                        generic_name=self.generic_name,
                        generic_type_range=self.generic_type_range,
                        struct_name=self.struct_name)
        tmp_type.isConst = self.isConst
        tmp_type.base_type_list = copy.deepcopy(self.base_type_list)
        tmp_type.dims = copy.deepcopy(self.dims)
        tmp_type.reference = self.reference
        tmp_type.func_ret_type = self.func_ret_type
        tmp_type.func_params = copy.deepcopy(self.func_params)
        tmp_type.generics_type_list = [*self.generics_type_list]
        if clone_symbol_table:
            tmp_type.symbol_table = self.symbol_table.clone()
            # tmp_type.symbol_table.parent_type = tmp_type
        else:
            tmp_type.symbol_table = self.symbol_table
        tmp_type.unParsed = self.unParsed
        return tmp_type

    def __eq__(self, type: Type) -> bool:
        if not isinstance(type, Type):
            return False
        if self.get_dim_size() != type.get_dim_size():
            return False
        for dim1, dim2 in zip(self.dims, type.dims):
            if dim1 != dim2:
                return False
        kind1, kind2 = self.idType, type.idType
        if kind1 == IDType.AUTO and kind2 == IDType.AUTO:
            return True
        elif kind1 == IDType.BASIC and kind2 == IDType.BASIC:
            return self.basic_type == type.basic_type
        elif kind1 == IDType.GENERIC and kind2.GENERIC:
            return self.generic_name == type.generic_name
        elif kind1 == IDType.STRUCT and kind2 == IDType.STRUCT:
            return self.struct_name == type.struct_name
        elif kind1 == IDType.REFERENCE and kind2 == IDType.REFERENCE:
            return self.clone().remove_ref() == type.clone().remove_ref()
        elif kind1 == IDType.FUNCTION and kind2 == IDType.FUNCTION:
            if not (self.func_ret_type == type.func_ret_type):
                return False
            if len(self.func_params) != len(type.func_params):
                return False
            for param1, param2 in zip(self.func_params, type.func_params):
                if not (param1.type == param2.type):
                    return False
            return True

        return False

    def __str__(self) -> str:
        kind = self.idType

        def get_generic_str() -> str:
            if not self.has_generics():
                return ''
            generic_str = '<'
            for i, generics_type in enumerate(self.generics_type_list):
                if i > 0:
                    generic_str += ', '
                generic_str += f'{generics_type}' if generics_type.generic_name else '""'
            generic_str += '>'
            return generic_str

        if len(self.dims) > 0:
            element_type = self.clone().array_element()
            return f'[{self.get_array_size_chosen(-1)}]{element_type}'

        if kind == IDType.AUTO:
            return 'auto'
        if kind == IDType.BASIC:
            return self.basic_type.name
        elif kind == IDType.GENERIC:
            return self.generic_name
        elif kind == IDType.STRUCT:
            return f'struct {self.struct_name}{get_generic_str()}'
        elif kind == IDType.REFERENCE:
            refered_type = self.clone().remove_ref()
            return f'{refered_type} ref'
        elif kind == IDType.FUNCTION:
            func_str = f'{get_generic_str()}('
            for i, param in enumerate(self.func_params):
                if i > 0:
                    func_str += ', '
                func_str += f'{param.type}'
            func_str += f') -> {self.func_ret_type}'
            return func_str
        else:
            assert False

    # def to_ir_type(self) -> ir.Type:
    #     kind = self.get_idtype()
    #     if kind == IDType.AUTO:
    #         return ir.VoidType()
    #     if kind == IDType.BASIC:
    #         if self.basic_type == BasicType.VOID:
    #             return ir.VoidType()
    #         if self.basic_type == BasicType.BOOL:
    #             return ir.IntType(1)
    #         elif self.basic_type == BasicType.F16:
    #             return ir.HalfType()
    #         elif self.basic_type == BasicType.F32:
    #             return ir.FloatType()
    #         elif self.basic_type == BasicType.F64:
    #             return ir.DoubleType()
    #         elif self.basic_type == BasicType.I8 or self.basic_type == BasicType.U8:
    #             return ir.IntType(8)
    #         elif self.basic_type == BasicType.I16 or self.basic_type == BasicType.U16:
    #             return ir.IntType(16)
    #         elif self.basic_type == BasicType.I32 or self.basic_type == BasicType.U32:
    #             return ir.IntType(32)
    #         elif self.basic_type == BasicType.I64 or self.basic_type == BasicType.U64:
    #             return ir.IntType(64)
    #         else:
    #             raise NotImplementedError(f'IR BasicType {self.basic_type} not implemented')
    #     elif kind == IDType.STRUCT:
    #         return ir.global_context.get_identified_type(self.struct_name)
    #     elif kind == IDType.ARRAY:
    #         element_type = self.clone().to_element_type()
    #         element_ir_type = element_type.to_ir_type()
    #         # if element_type.get_kind() == IDType.BASIC:
    #         #     return ir.VectorType(element_ir_type, self.array_dims[-1])
    #         # else:
    #         return ir.ArrayType(element_ir_type, self.dims[-1])
    #     elif kind == IDType.REFERENCE:
    #         refered_ir_type = self.clone().remove_ref().to_ir_type()
    #         return ir.PointerType(refered_ir_type)
    #     elif kind == IDType.FUNCTION:  # Return Function Pointer IR type
    #         ret_ir_type = self.func_ret_type.to_ir_type()
    #         param_ir_types = []
    #         for param in self.func_params:
    #             param_ir_types.append(param.type.to_ir_type())
    #         return ir.PointerType(ir.FunctionType(ret_ir_type, param_ir_types))
    #     else:
    #         assert False, "uninstantiabled type!"
    #
    # def match_generics(self, spec_type: Type) -> Tuple[bool, Dict[str, Type]]:
    #     """模版类型与函数实参匹配，推导出模版类型"""
    #     kind1, kind2 = self.get_idtype(), spec_type.get_idtype()
    #     if kind1 == IDType.GENERIC and kind2 != IDType.GENERIC:
    #         # Matched generics type with a specializaed type
    #         return True, {self.generic_name: spec_type}
    #     elif kind1 == IDType.AUTO and kind2 == IDType.AUTO:
    #         return True, {}
    #     elif kind1 == IDType.BASIC and kind2 == IDType.BASIC:
    #         return self.basic_type == spec_type.basic_type, {}
    #     elif kind1 == IDType.STRUCT and kind2 == IDType.STRUCT:
    #         return self.struct_name == spec_type.struct_name, {}
    #     elif kind1 == IDType.ARRAY and kind2 == IDType.ARRAY:
    #         return self.clone().to_element_type().match_generics(spec_type.clone().to_element_type())
    #     elif kind1 == IDType.REFERENCE and kind2 == IDType.REFERENCE:
    #         return self.clone().remove_ref().match_generics(spec_type.clone().remove_ref())
    #     elif kind1 == IDType.FUNCTION and kind2 == IDType.FUNCTION:
    #         if len(self.func_params) != len(spec_type.func_params):
    #             return False, {}
    #         ret, all_matched = self.func_ret_type.match_generics(spec_type.func_ret_type)
    #         if not ret:
    #             return False, {}
    #         for param1, param2 in zip(self.func_params, spec_type.func_params):
    #             ret, matched = param1.type.match_generics(param2.type)
    #             if not ret:
    #                 return False, {}
    #             all_matched = merge_matched(all_matched, matched)
    #             if all_matched is None:
    #                 return False, {}
    #         return True, all_matched
    #     else:
    #         return False, {}
    #
    # def specialize(self, generic_specialization_list: Dict[str, Type], spec_param_array_dims: Optional[Dict[str, List[int]]] = None) -> Type:
    #     """将该类型中嵌套的泛型类型按照实例化列表进行替换"""
    #     kind = self.get_idtype()
    #
    #     if kind == IDType.AUTO:
    #         return self
    #     if kind == IDType.BASIC:
    #         return self
    #     elif kind == IDType.GENERIC:
    #         if self.generic_name in generic_specialization_list:
    #             return generic_specialization_list[self.generic_name]
    #         else:
    #             return self
    #     elif kind == IDType.STRUCT:
    #         return self
    #     elif kind == IDType.ARRAY:
    #         element_type = self.clone().to_element_type()
    #         return element_type.specialize(generic_specialization_list).clone().add_array_dim_chosen(self.get_array_size())
    #     elif kind == IDType.REFERENCE:
    #         refered_type = self.clone().remove_ref()
    #         return refered_type.specialize(generic_specialization_list).clone().add_ref()
    #     elif kind == IDType.FUNCTION:
    #         func_type = self.clone(clone_symbol_table=True)
    #         func_type.func_ret_type = self.func_ret_type.specialize(generic_specialization_list)
    #         for i, param_symbol in enumerate(self.func_params):
    #             param_type = param_symbol.type.specialize(generic_specialization_list)
    #             # 实例化数组维数
    #             if spec_param_array_dims is not None and len(param_type.dims) > 0 and param_symbol.id in spec_param_array_dims:
    #                 param_type = param_type.clone()
    #                 array_dims = spec_param_array_dims[param_symbol.id]
    #                 for i, dim in enumerate(param_type.dims):
    #                     if dim == 0:
    #                         param_type.dims[i] = array_dims[i]
    #             new_param_symbol = func_type.symbol_table.replace_local_symbol_type(param_symbol.id, param_type)
    #             func_type.func_params[i] = new_param_symbol
    #         for generic_name, spec_type in generic_specialization_list.items():
    #             assert len(generic_name) > 0
    #             func_type.symbol_table.replace_local_type(generic_name, spec_type)
    #         return func_type
    #     else:
    #         assert False
