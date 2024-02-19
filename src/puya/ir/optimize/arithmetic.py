import operator
from collections.abc import Callable
from functools import partial
from itertools import zip_longest

import attrs
import structlog

from puya.avm_type import AVMType
from puya.context import CompileContext
from puya.ir import models, visitor
from puya.ir.avm_ops import AVMOp
from puya.ir.optimize._utils import get_definition
from puya.ir.types_ import AVMBytesEncoding
from puya.ir.utils import format_bytes
from puya.parse import SourceLocation
from puya.utils import itob_eval

logger: structlog.typing.FilteringBoundLogger = structlog.get_logger(__name__)


def get_int_constant(value: models.ValueProvider) -> int | None:
    if isinstance(value, models.UInt64Constant):
        return value.value
    return None


def get_biguint_constant(value: models.ValueProvider) -> int | None:
    if isinstance(value, models.BigUIntConstant):
        return value.value
    if isinstance(value, models.BytesConstant) and len(value.value) <= 64:
        return int.from_bytes(value.value, byteorder="big", signed=False)
    return None


def byte_wise(op: Callable[[int, int], int], lhs: bytes, rhs: bytes) -> bytes:
    return bytes([op(a, b) for a, b in zip_longest(lhs[::-1], rhs[::-1], fillvalue=0)][::-1])


def _format_bytes_const(bytes_const: models.BytesConstant) -> str:
    return format_bytes(bytes_const.value, bytes_const.encoding)


def _choose_encoding(a: models.BytesConstant, b: models.BytesConstant) -> AVMBytesEncoding:
    if a.encoding == b.encoding:
        # preserve encoding if both equal
        return a.encoding
    else:
        # go with most compact if they differ
        return AVMBytesEncoding.base64


def _concat(
    a: models.BytesConstant, b: models.BytesConstant, source_location: SourceLocation | None
) -> models.BytesConstant:
    target_encoding = _choose_encoding(a, b)
    result_value = a.value + b.value
    result = models.BytesConstant(
        value=result_value,
        encoding=target_encoding,
        source_location=source_location,
    )
    logger.debug(
        f"Folded concat of {_format_bytes_const(a)} and {_format_bytes_const(b)}"
        f" to {_format_bytes_const(result)}"
    )
    return result


def get_byte_constant(
    subroutine: models.Subroutine, byte_arg: models.Value
) -> models.BytesConstant | None:
    if isinstance(byte_arg, models.BytesConstant):
        return byte_arg
    if isinstance(byte_arg, models.BigUIntConstant):
        return models.BytesConstant(
            source_location=byte_arg.source_location,
            value=itob_eval(byte_arg.value),
            encoding=AVMBytesEncoding.base16,
        )
    if isinstance(byte_arg, models.Register):
        byte_arg_defn = get_definition(subroutine, byte_arg)
        if isinstance(byte_arg_defn, models.Assignment) and isinstance(
            byte_arg_defn.source, models.Intrinsic
        ):
            match byte_arg_defn.source:
                case models.Intrinsic(op=AVMOp.itob, args=[models.UInt64Constant(value=itob_arg)]):
                    return models.BytesConstant(
                        source_location=byte_arg_defn.source_location,
                        value=itob_arg.to_bytes(8, "big"),
                        encoding=AVMBytesEncoding.base16,
                    )
                case models.Intrinsic(
                    op=AVMOp.bzero, args=[models.UInt64Constant(value=bzero_arg)]
                ) if bzero_arg <= 64:
                    return models.BytesConstant(
                        source_location=byte_arg_defn.source_location,
                        value=b"\x00" * bzero_arg,
                        encoding=AVMBytesEncoding.base16,
                    )
    return None


def try_simplify_arithmetic_ops(
    subroutine: models.Subroutine, intrinsic: models.Intrinsic
) -> models.ValueProvider | None:
    # TODO: handle bytes math
    # TODO: handle all math ops including shl, shr, exp, etc
    op_loc = intrinsic.source_location
    if intrinsic.op is AVMOp.not_:
        x = get_int_constant(intrinsic.args[0])
        if x is not None:
            not_x = models.UInt64Constant(source_location=op_loc, value=0 if x else 1)
            logger.debug(f"Folded !{x} to {not_x}")
            return not_x
    elif intrinsic.op is AVMOp.bitwise_not:
        x = get_int_constant(intrinsic.args[0])
        if x is not None:
            not_x = models.UInt64Constant(source_location=op_loc, value=x ^ 0xFFFFFFFFFFFFFFFF)
            logger.debug(f"Folded ~{x} to {not_x}")
            return not_x
    elif intrinsic.op is AVMOp.bitwise_not_bytes:
        byte_const = get_byte_constant(subroutine, intrinsic.args[0])
        if byte_const is not None:
            not_bites = models.BytesConstant(
                source_location=op_loc,
                value=bytes([x ^ 0xFF for x in byte_const.value]),
                encoding=byte_const.encoding,
            )
            logger.debug(f"Folded ~{byte_const.value!r} to {not_bites.value!r}")
            return not_bites
    elif intrinsic.op is AVMOp.btoi:
        byte_const = get_byte_constant(subroutine, intrinsic.args[0])
        if byte_const is not None:
            return models.UInt64Constant(
                value=int.from_bytes(byte_const.value, byteorder="big", signed=False),
                source_location=op_loc,
            )
    elif intrinsic.op is AVMOp.setbit:
        match intrinsic.args:
            case [
                byte_arg,
                models.UInt64Constant() as index,
                models.UInt64Constant() as value,
            ] if (byte_const := get_byte_constant(subroutine, byte_arg)) is not None:
                binary_array = [
                    x for xs in [bin(bb)[2:].zfill(8) for bb in byte_const.value] for x in xs
                ]
                binary_array[index.value] = "1" if value.value else "0"
                binary_string = "".join(binary_array)
                adjusted_const_value = int(binary_string, 2).to_bytes(
                    len(byte_const.value), byteorder="big"
                )
                return models.BytesConstant(
                    source_location=op_loc,
                    encoding=byte_const.encoding,
                    value=adjusted_const_value,
                )
    elif intrinsic.op is AVMOp.getbit:
        match intrinsic.args:
            case [byte_arg, models.UInt64Constant() as index] if (
                byte_const := get_byte_constant(subroutine, byte_arg)
            ) is not None:
                binary_array = [
                    x for xs in [bin(bb)[2:].zfill(8) for bb in byte_const.value] for x in xs
                ]
                the_bit = binary_array[index.value]
                return models.UInt64Constant(source_location=op_loc, value=int(the_bit))
    elif intrinsic.op.code.startswith("extract_uint"):
        match intrinsic.args:
            case [
                models.BytesConstant(value=bytes_value),
                models.UInt64Constant(value=offset),
            ]:
                bit_size = int(intrinsic.op.code.removeprefix("extract_uint"))
                byte_size = bit_size // 8
                extracted = bytes_value[offset : offset + byte_size]
                if len(extracted) != byte_size:
                    return None  # would fail at runtime, lets hope this is unreachable 😬
                uint64_result = int.from_bytes(extracted, byteorder="big", signed=False)
                return models.UInt64Constant(
                    value=uint64_result,
                    source_location=op_loc,
                )
    elif intrinsic.op is AVMOp.len_:
        byte_const = get_byte_constant(subroutine, intrinsic.args[0])
        if byte_const is not None:
            len_x = len(byte_const.value)
            logger.debug(f"Folded len({_format_bytes_const(byte_const)}) to {len_x}")
            return models.UInt64Constant(source_location=op_loc, value=len_x)
    elif intrinsic.op is AVMOp.concat:
        left_arg, right_arg = intrinsic.args
        left_const = get_byte_constant(subroutine, left_arg)
        right_const = get_byte_constant(subroutine, right_arg)
        if left_const is not None:
            if left_const.value == b"":
                return right_arg
            if right_const is not None:
                # two constants, just fold
                return _concat(left_const, right_const, source_location=op_loc)
        elif right_const is not None:
            if right_const.value == b"":
                return left_arg
            if (
                # left constant concats will automatically get folded, like "a" + "b" + var because
                # of the way they're linearized, but var + "a" + "b" won't be so we special case it
                isinstance(left_arg, models.Register)
                and (left_arg_defn := get_definition(subroutine, left_arg)) is not None
                and isinstance(left_arg_defn, models.Assignment)
                and isinstance(left_arg_defn.source, models.Intrinsic)
                and left_arg_defn.source.op is AVMOp.concat
                and isinstance(prev_concat_lhs := left_arg_defn.source.args[0], models.Register)
                and isinstance(
                    maybe_byte_const_a := left_arg_defn.source.args[1], models.BytesConstant
                )
            ):
                location = right_const.source_location or maybe_byte_const_a.source_location
                return attrs.evolve(
                    intrinsic,
                    args=[
                        prev_concat_lhs,
                        _concat(maybe_byte_const_a, right_const, source_location=location),
                    ],
                )
    else:
        match intrinsic:
            case models.Intrinsic(
                op=AVMOp.extract | AVMOp.extract3,
                immediates=[int(S), int(L)],
                args=[byte_arg],
                source_location=op_loc,
            ) | models.Intrinsic(
                op=AVMOp.extract | AVMOp.extract3,
                immediates=[],
                args=[byte_arg, models.UInt64Constant(value=S), models.UInt64Constant(value=L)],
                source_location=op_loc,
            ) if (
                byte_const := get_byte_constant(subroutine, byte_arg)
            ) is not None:
                if L == 0:
                    extracted = byte_const.value[S:]
                else:
                    extracted = byte_const.value[S : S + L]
                return models.BytesConstant(
                    source_location=op_loc, encoding=byte_const.encoding, value=extracted
                )
            case models.Intrinsic(
                op=AVMOp.substring | AVMOp.substring3,
                immediates=[int(S), int(E)],
                args=[byte_arg],
                source_location=op_loc,
            ) | models.Intrinsic(
                op=AVMOp.substring | AVMOp.substring3,
                immediates=[],
                args=[byte_arg, models.UInt64Constant(value=S), models.UInt64Constant(value=E)],
                source_location=op_loc,
            ) if (
                byte_const := get_byte_constant(subroutine, byte_arg)
            ) is not None:
                if E < S:
                    return None  # would fail at runtime, lets hope this is unreachable 😬
                extracted = byte_const.value[S:E]
                return models.BytesConstant(
                    source_location=op_loc, encoding=byte_const.encoding, value=extracted
                )
            case models.Intrinsic(
                op=(
                    AVMOp.eq
                    | AVMOp.neq
                    | AVMOp.bitwise_and_bytes
                    | AVMOp.bitwise_or_bytes
                    | AVMOp.bitwise_xor_bytes
                ) as bytes_op,
                args=[byte_arg_a, byte_arg_b],
                source_location=op_loc,
            ) if (
                (byte_const_a := get_byte_constant(subroutine, byte_arg_a)) is not None
                and (byte_const_b := get_byte_constant(subroutine, byte_arg_b)) is not None
            ):
                bytes_a = byte_const_a.value
                bytes_b = byte_const_b.value
                if bytes_op == AVMOp.eq:
                    return models.UInt64Constant(
                        value=int(bytes_a == bytes_b), source_location=op_loc
                    )
                elif bytes_op == AVMOp.neq:
                    return models.UInt64Constant(
                        value=int(bytes_a != bytes_b), source_location=op_loc
                    )
                else:
                    target_encoding = _choose_encoding(byte_const_a, byte_const_b)
                    do_op = {
                        AVMOp.bitwise_and_bytes: operator.and_,
                        AVMOp.bitwise_or_bytes: operator.or_,
                        AVMOp.bitwise_xor_bytes: operator.xor,
                    }[bytes_op]
                    return models.BytesConstant(
                        value=byte_wise(do_op, bytes_a, bytes_b),
                        encoding=target_encoding,
                        source_location=op_loc,
                    )
            case models.Intrinsic(
                args=[
                    models.Register(atype=AVMType.uint64) as reg_a,
                    models.Register(atype=AVMType.uint64) as reg_b,
                ],
                op=op,
            ):
                c: models.Value | int | None = None
                if reg_a == reg_b:
                    match op:
                        case AVMOp.sub:
                            c = 0
                        case AVMOp.eq | AVMOp.lte | AVMOp.gte:
                            c = 1
                        case AVMOp.neq:
                            c = 0
                        case AVMOp.div_floor:
                            c = 1
                        case AVMOp.bitwise_xor:
                            c = 0
                        case AVMOp.bitwise_and | AVMOp.bitwise_or:
                            c = reg_a
                if c is not None:
                    if isinstance(c, models.Value):
                        logger.debug(f"Folded {reg_a} {op} {reg_b} to {c}")
                        return c
                    else:
                        logger.debug(f"Folded {reg_a} {op} {reg_b} to {c}")
                        return models.UInt64Constant(
                            value=c, source_location=intrinsic.source_location
                        )
            case models.Intrinsic(
                args=[
                    models.Value(atype=AVMType.uint64) as a,
                    models.Value(atype=AVMType.uint64) as b,
                ],
                op=op,
            ):
                c = None
                a_const = get_int_constant(a)
                b_const = get_int_constant(b)
                # 0 == b <-> !b
                if a_const == 0 and op == AVMOp.eq:
                    return attrs.evolve(intrinsic, op=AVMOp.not_, args=[b])
                # a == 0 <-> !a
                elif b_const == 0 and op == AVMOp.eq:
                    return attrs.evolve(intrinsic, op=AVMOp.not_, args=[a])
                # TODO: can we somehow do the below only in a boolean context?
                # # 0 != b <-> b
                # elif a_const == 0 and op == AVMOp.neq:
                #     c = b
                # # a != 0 <-> a
                # elif b_const == 0 and op == AVMOp.neq:
                #     c = a
                elif a_const == 1 and op == AVMOp.mul:
                    c = b
                elif b_const == 1 and op == AVMOp.mul:
                    c = a
                elif a_const == 0 and op in (AVMOp.add, AVMOp.or_):
                    c = b
                elif b_const == 0 and op in (AVMOp.add, AVMOp.sub, AVMOp.or_):
                    c = a
                elif 0 in (a_const, b_const) and op in (AVMOp.mul, AVMOp.and_):
                    c = 0
                elif a_const is not None and b_const is not None:
                    match op:
                        case AVMOp.add:
                            c = a_const + b_const
                        case AVMOp.sub:
                            c = a_const - b_const
                        case AVMOp.mul:
                            c = a_const * b_const
                        case AVMOp.div_floor if b_const != 0:
                            c = a_const // b_const
                        case AVMOp.mod if b_const != 0:
                            c = a_const % b_const
                        case AVMOp.lt:
                            c = 1 if a_const < b_const else 0
                        case AVMOp.lte:
                            c = 1 if a_const <= b_const else 0
                        case AVMOp.gt:
                            c = 1 if a_const > b_const else 0
                        case AVMOp.gte:
                            c = 1 if a_const >= b_const else 0
                        case AVMOp.eq:
                            c = 1 if a_const == b_const else 0
                        case AVMOp.neq:
                            c = 1 if a_const != b_const else 0
                        case AVMOp.and_:
                            c = int(a_const and b_const)
                        case AVMOp.or_:
                            c = int(a_const or b_const)
                        case AVMOp.shl:
                            c = (a_const << b_const) % (2**64)
                        case AVMOp.shr:
                            c = a_const >> b_const
                        case AVMOp.exp:
                            if a_const == 0 and b_const == 0:
                                return (
                                    None  # would fail at runtime, lets hope this is unreachable 😬
                                )
                            c = a_const**b_const
                        case AVMOp.bitwise_or:
                            c = a_const | b_const
                        case AVMOp.bitwise_and:
                            c = a_const & b_const
                        case AVMOp.bitwise_xor:
                            c = a_const ^ b_const
                if c is not None:
                    if isinstance(c, models.ValueProvider):
                        logger.debug(f"Folded {a} {op} {b} to {c}")
                        return c
                    else:
                        if c < 0:
                            # Value cannot be folded as it would result in a negative uint
                            return None
                        logger.debug(
                            f"Folded {a_const if a_const is not None else a}"
                            f" {op} {b_const if b_const is not None else b} to {c}"
                        )
                        return models.UInt64Constant(
                            value=c, source_location=intrinsic.source_location
                        )
            case models.Intrinsic(
                args=[
                    models.Register(atype=AVMType.bytes) as reg_a,
                    models.Register(atype=AVMType.bytes) as reg_b,
                ],
                op=op,
            ):
                c = None
                if reg_a == reg_b:
                    match op:
                        case AVMOp.sub_bytes:
                            c = 0
                        case AVMOp.eq_bytes | AVMOp.eq:
                            c = 1
                        case AVMOp.neq_bytes | AVMOp.neq:
                            c = 0
                        case AVMOp.div_floor_bytes:
                            c = 1
                if c is not None:
                    if isinstance(c, models.Value):
                        logger.debug(f"Folded {reg_a} {op} {reg_b} to {c}")
                        return c
                    else:
                        logger.debug(f"Folded {reg_a} {op} {reg_b} to {c}")
                        return models.UInt64Constant(
                            value=c, source_location=intrinsic.source_location
                        )
            case models.Intrinsic(
                args=[
                    models.Value(atype=AVMType.bytes) as a,
                    models.Value(atype=AVMType.bytes) as b,
                ],
                op=op,
            ):
                c = None
                a_const = get_biguint_constant(a)
                b_const = get_biguint_constant(b)
                if a_const == 1 and op == AVMOp.mul_bytes:
                    c = b
                elif b_const == 1 and op == AVMOp.mul_bytes:
                    c = a
                elif a_const == 0 and op == AVMOp.add_bytes:
                    c = b
                elif b_const == 0 and op in (AVMOp.add_bytes, AVMOp.sub_bytes):
                    c = a
                elif 0 in (a_const, b_const) and op == AVMOp.mul_bytes:
                    c = 0
                elif a_const is not None and b_const is not None:
                    match op:
                        case AVMOp.add_bytes:
                            c = a_const + b_const
                        case AVMOp.sub_bytes:
                            c = a_const - b_const
                        case AVMOp.mul_bytes:
                            c = a_const * b_const
                        case AVMOp.div_floor_bytes:
                            c = a_const // b_const
                        case AVMOp.lt_bytes:
                            c = 1 if a_const < b_const else 0
                        case AVMOp.lte_bytes:
                            c = 1 if a_const <= b_const else 0
                        case AVMOp.gt_bytes:
                            c = 1 if a_const > b_const else 0
                        case AVMOp.gte_bytes:
                            c = 1 if a_const >= b_const else 0
                        case AVMOp.eq_bytes | AVMOp.eq:
                            c = 1 if a_const == b_const else 0
                        case AVMOp.neq_bytes | AVMOp.neq:
                            c = 1 if a_const != b_const else 0
                if c is not None:
                    if isinstance(c, models.ValueProvider):
                        logger.debug(f"Folded {a} {op} {b} to {c}")
                        return c
                    logger.debug(
                        f"Folded {a_const if a_const is not None else a}"
                        f" {op} {b_const if b_const is not None else b} to {c}"
                    )
                    if op in (
                        AVMOp.eq_bytes,
                        AVMOp.eq,
                        AVMOp.neq_bytes,
                        AVMOp.neq,
                        AVMOp.lt_bytes,
                        AVMOp.lte_bytes,
                        AVMOp.gt_bytes,
                        AVMOp.gte_bytes,
                    ):
                        return models.UInt64Constant(
                            value=c, source_location=intrinsic.source_location
                        )
                    else:
                        return models.BigUIntConstant(
                            value=c, source_location=intrinsic.source_location
                        )

    return None


def _make_uint64_folder(
    op_callback: Callable[[int, int], int]
) -> Callable[[int, int, SourceLocation | None], models.UInt64Constant]:
    def folder(
        lhs: int, rhs: int, source_location: SourceLocation | None
    ) -> models.UInt64Constant:
        value = op_callback(lhs, rhs)
        return models.UInt64Constant(value=value, source_location=source_location)

    return folder


def _make_biguint_folder(
    op_callback: Callable[[int, int], int]
) -> Callable[[int, int, SourceLocation | None], models.BigUIntConstant]:
    def folder(
        lhs: int, rhs: int, source_location: SourceLocation | None
    ) -> models.BigUIntConstant:
        value = op_callback(lhs, rhs)
        return models.BigUIntConstant(value=value, source_location=source_location)

    return folder


def _make_bytes_folder(
    op_callback: Callable[[int, int], int]
) -> Callable[
    [models.BytesConstant, models.BytesConstant, SourceLocation | None], models.BytesConstant
]:
    def folder(
        lhs: models.BytesConstant,
        rhs: models.BytesConstant,
        source_location: SourceLocation | None,
    ) -> models.BytesConstant:
        value = byte_wise(op_callback, lhs.value, rhs.value)
        encoding = _choose_encoding(lhs, rhs)
        return models.BytesConstant(
            value=value, encoding=encoding, source_location=source_location
        )

    return folder


def arithmetic_simplification(_context: CompileContext, subroutine: models.Subroutine) -> bool:
    """Simplify arithmetic expressions e.g. a-a -> 0, a*0 -> 0, a*1 -> a"""
    modified = 0

    _get_byte_constant = partial(get_byte_constant, subroutine)

    commutative_ops = {
        "+": (get_int_constant, _make_uint64_folder(operator.add)),
        "*": (get_int_constant, _make_uint64_folder(operator.mul)),
        "&": (get_int_constant, _make_uint64_folder(operator.and_)),
        "|": (get_int_constant, _make_uint64_folder(operator.or_)),
        "^": (get_int_constant, _make_uint64_folder(operator.xor)),
        "b+": (get_biguint_constant, _make_biguint_folder(operator.add)),
        "b*": (get_biguint_constant, _make_biguint_folder(operator.mul)),
        "b&": (_get_byte_constant, _make_bytes_folder(operator.and_)),
        "b|": (_get_byte_constant, _make_bytes_folder(operator.or_)),
        "b^": (_get_byte_constant, _make_bytes_folder(operator.xor)),
        # "concat": (_get_byte_constant, _concat),
    }

    for block in subroutine.body:
        for op in block.ops:
            match op:
                case models.Assignment(source=models.Intrinsic() as source) as assignment:
                    simplified = try_simplify_arithmetic_ops(subroutine, source)
                    if simplified is not None:
                        assignment.source = simplified
                        modified += 1
                    elif source.op.code in commutative_ops:
                        const_getter, folder = commutative_ops[source.op.code]
                        curr_lhs, curr_rhs = source.args
                        # if one operand is a constant but not the other
                        curr_lhs_const = const_getter(curr_lhs)
                        curr_rhs_const = const_getter(curr_rhs)
                        if (curr_lhs_const is None) != (curr_rhs_const is None):
                            if curr_lhs_const is not None:
                                assert isinstance(curr_rhs, models.Register)
                                the_reg = curr_rhs
                                constant1 = curr_lhs_const
                                constant1_loc = curr_lhs.source_location
                            else:
                                assert isinstance(curr_lhs, models.Register)
                                the_reg = curr_lhs
                                constant1 = curr_rhs_const
                                constant1_loc = curr_rhs.source_location
                            the_reg_usage_count = RegisterUsageCounter.collect(
                                subroutine, find=the_reg
                            )
                            # can we (definitely) eliminate the_reg if we fold?
                            if the_reg_usage_count == 1:
                                reg_defn = get_definition(subroutine, the_reg)
                                if (
                                    isinstance(reg_defn, models.Assignment)
                                    and isinstance(reg_defn.source, models.Intrinsic)
                                    and reg_defn.source.op == source.op
                                ):
                                    prev_op = reg_defn.source
                                    prev_lhs, prev_rhs = prev_op.args
                                    prev_lhs_const = const_getter(prev_lhs)
                                    prev_rhs_const = const_getter(prev_rhs)
                                    if (prev_lhs_const is None) != (prev_rhs_const is None):
                                        if prev_lhs_const is not None:
                                            assert isinstance(prev_rhs, models.Register)
                                            the_reg_to_keep = prev_rhs
                                            constant2 = prev_lhs_const
                                            constant2_loc = prev_lhs.source_location
                                        else:
                                            assert isinstance(prev_lhs, models.Register)
                                            the_reg_to_keep = prev_lhs
                                            constant2 = prev_rhs_const
                                            constant2_loc = prev_rhs.source_location
                                        folded_location = constant1_loc or constant2_loc
                                        folded_const = folder(
                                            constant1, constant2, folded_location
                                        )
                                        modified += 1
                                        logger.debug(
                                            f"Triplet with {source.op.code} ({source.op}, {prev_op}) folded to ({the_reg_to_keep} {folded_const})"
                                        )
                                        assignment.source = attrs.evolve(
                                            source, args=[the_reg_to_keep, folded_const]
                                        )

                        # # left constant concats will automatically get folded, like "a" + "b" + var because
                        # # reg = "a" + "b"
                        # # reg2 = reg + var
                        # # of the way they're linearized, but var + "a" + "b" won't be so we special case it
                        # # reg = var + "a"
                        # # reg2 = reg + "b" -> reg2 = var + ("a" + "b")
                        # # TODO: "a" + var + "b" -> var + ("a" + "b") for associative+commutative ops
                        # if len(source.args) == 2:
                        #     source_lhs, source_rhs = source.args
                        #     if (
                        #         isinstance(source_lhs, models.Register)
                        #         and (source_rhs_const := const_getter(source_rhs)) is not None
                        #     ):
                        #         source_lhs_usage_count = RegisterUsageCounter.collect(
                        #             subroutine, find=source_lhs
                        #         )
                        #         if source_lhs_usage_count == 1:
                        #             lhs_defn = get_definition(subroutine, source_lhs)
                        #             if isinstance(lhs_defn, models.Assignment):
                        #                 prev_source = lhs_defn.source
                        #                 if (
                        #                     isinstance(prev_source, models.Intrinsic)
                        #                     and prev_source.op == source.op
                        #                     and len(prev_source.args) == 2
                        #                 ):
                        #                     prev_lhs, prev_rhs = prev_source.args
                        #                     if (
                        #                         isinstance(prev_lhs, models.Register)
                        #                         and (prev_rhs_const := const_getter(prev_rhs))
                        #                         is not None
                        #                     ):
                        #                         folded_location = (
                        #                             source_rhs.source_location
                        #                             or prev_rhs.source_location
                        #                         )
                        #                         folded = folder(
                        #                             prev_rhs_const,
                        #                             source_rhs_const,
                        #                             folded_location,
                        #                         )
                        #                         logger.debug(
                        #                             f"Triplet with {source.op.code} ({prev_lhs} {prev_rhs_const} {source_rhs_const}) optimised to ({prev_lhs} {folded})"
                        #                         )
                        #                         assignment.source = attrs.evolve(
                        #                             source, args=[prev_lhs, folded]
                        #                         )
                        #                         modified += 1
                        #                     elif (
                        #                         source.op.code != "concat"
                        #                         and isinstance(prev_rhs, models.Register)
                        #                         and (prev_lhs_const := const_getter(prev_lhs))
                        #                         is not None
                        #                     ):
                        #                         folded_location = (
                        #                             source_rhs.source_location
                        #                             or prev_lhs.source_location
                        #                         )
                        #                         folded = folder(
                        #                             prev_lhs_const,
                        #                             source_rhs_const,
                        #                             folded_location,
                        #                         )
                        #                         logger.debug(
                        #                             f"Triplet with {source.op.code} ({prev_lhs} {prev_lhs_const} {source_rhs_const}) optimised to ({prev_lhs} {folded})"
                        #                         )
                        #                         assignment.source = attrs.evolve(
                        #                             source, args=[prev_lhs, folded]
                        #                         )
                        #                         modified += 1

    return modified > 0


def _can_get_constant(subroutine: models.Subroutine, source: models.Value) -> bool:
    match source.atype:
        case AVMType.uint64:
            return get_int_constant(source) is not None
        case AVMType.bytes:
            return (
                get_biguint_constant(source) is not None
                or get_byte_constant(subroutine, source) is not None
            )
    return False


@attrs.define
class RegisterUsageCounter(visitor.IRTraverser):
    find: models.Register
    count: int = attrs.field(default=0, init=False)

    @classmethod
    def collect(cls, sub: models.Subroutine, find: models.Register) -> int:
        counter = cls(find=find)
        counter.visit_all_blocks(sub.body)
        return counter.count

    def visit_register(self, reg: models.Register) -> None:
        if reg == self.find:
            self.count += 1

    def visit_phi(self, phi: models.Phi) -> None:
        for arg in phi.args:
            arg.accept(self)

    def visit_assignment(self, ass: models.Assignment) -> None:
        ass.source.accept(self)
