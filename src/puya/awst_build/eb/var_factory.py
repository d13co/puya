from puya.awst.nodes import Expression
from puya.awst_build.eb.base import NodeBuilder


def var_expression(expr: Expression) -> NodeBuilder:
    from puya.awst_build.eb import type_registry

    return type_registry.var_expression(expr)
