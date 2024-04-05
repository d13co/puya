from __future__ import annotations

import typing

import attrs

from puya import algo_constants, log
from puya.avm_type import AVMType
from puya.errors import InternalError

logger = log.get_logger(__name__)


# StackType describes the type of a value on the operand stack
@attrs.define
class StackType:
    name: str  # alias (address, boolean, ...) or derived name [5]byte
    avm_type: AVMType | None
    bound: tuple[int, int]  # represents max/min value for uint64 or max/min length for byte[]


StackNone: typing.Final = StackType(avm_type=None, bound=(-1, -1), name="none")
StackAny: typing.Final = StackType(avm_type=AVMType.any, bound=(0, 0), name="any")


# StackZeroUint64 is a StackUint64 with a minimum value of 0 and a maximum value of 0
StackZeroUint64: typing.Final = StackType(avm_type=AVMType.uint64, bound=(0, 0), name="0")


def assemble_string_with_version(text: str, version: int) -> OpStream:
    ops = OpStream(version=version)
    ops.assemble(text)
    return ops


@attrs.define
class LabelRef:
    position: int
    """position (PC) of the label reference"""
    label: Token
    """token holding the label name (and line, column)"""
    offset_position: int
    """ending position of the opcode containing the label reference"""


class ConstReference(typing.Protocol):
    value: int | bytes
    position: int
    """position of the opcode start that declares the int value"""

    def length(self, ops: OpStream, assembled: bytes) -> int:
        """get the length of the op for this reference in ops.pending"""

    def make_new_reference(self, ops: OpStream, singleton: bool, new_index: int) -> bytes:
        """create the opcode bytes for a new reference of the same value"""


@attrs.define
class IntReference(ConstReference):
    value: int = attrs.field(validator=[attrs.validators.ge(0), attrs.validators.lt(2**64)])
    position: int


@attrs.define
class ByteReference(ConstReference):
    value: bytes = attrs.field(validator=attrs.validators.max_len(algo_constants.MAX_BYTES_LENGTH))
    position: int


@attrs.define
class LabelReference:
    # position (PC) of the label reference
    position: int

    # token holding the label name (and line, column)
    label: Token

    # ending position of the opcode containing the label reference.
    offset_position: int


# SourceLocation points to a specific location in a source file.
@attrs.frozen
class TealSourceLocation:
    # Line is the line number, starting at 0.
    line: int
    # Column is the column number, starting at 0.
    column: int


@attrs.define
# ProgramKnowledge tracks statically known information as we assemble
class ProgramKnowledge:
    # list of the types known to be on the value stack, based on specs of
    # opcodes seen while assembling. In normal code, the tip of the stack must
    # match the next opcode's Arg.Types, and is then replaced with its
    # Return.Types. If `deadcode` is true, `stack` should be empty.
    stack: list[StackType] = attrs.field(factory=list)

    # bottom is the type given out when `stack` is empty. It is StackNone at
    # program start, so, for example, a `+` opcode at the start of a program
    # fails. But when a label or callsub is encountered, `stack` is truncated
    # and `bottom` becomes StackAny, because we don't track program state
    # coming in from elsewhere. A `+` after a label succeeds, because the stack
    # "virtually" contains an infinite list of StackAny.
    bottom: StackType = StackNone

    # deadcode indicates that the program is in deadcode, so no type checking
    # errors should be reported.
    deadcode: bool = False

    # fp is the frame pointer, if known/usable, or -1 if not.  When
    # encountering a `proto`, `stack` is grown to fit `args`, and this `fp` is
    # set to the top of those args.  This may not be the "real" fp when the
    # program is actually evaluated, but it is good enough for frame_{dig/bury}
    # to work from there.
    fp: int = -1

    scratch_space: list[StackType] = attrs.field(
        factory=lambda: [StackZeroUint64] * (algo_constants.MAX_SCRATCH_SLOT_NUMBER + 1)
    )

    # label resets knowledge to reflect that control may enter from elsewhere.
    def label(self) -> None:
        if self.deadcode:
            self.reset()

    #  reset clears existing knowledge and permissively allows any stack value.
    #  It's intended to be invoked after encountering a label or pragma type tracking change.
    def reset(self) -> None:
        self.stack = []
        self.bottom = StackAny
        self.fp = -1
        self.deadcode = False
        self.scratch_space = [StackAny] * (algo_constants.MAX_SCRATCH_SLOT_NUMBER + 1)

    def deaden(self) -> None:
        self.stack = self.stack[:0]  # ??
        self.deadcode = True


ASSEMBLER_DEFAULT_VERSION = 1


@attrs.define
class OpSpec:
    name: str
    mode: typing.Literal["app", "sig", "any"]
    arg_types: list[StackType]
    return_types: list[StackType]
    refine: typing.Callable[
        [ProgramKnowledge, list[Token]], tuple[list[StackType] | None, list[StackType] | None]
    ] | None

    def deadens(self) -> bool:
        return self.name in ("b", "callsub", "retsub", "err", "return")


def prepare_versioned_pseudo_table(version: int) -> dict[str, dict[int, OpSpec]]:
    raise NotImplementedError


@attrs.define
class OpStream:
    version: int | None  # None means rely on pragma or default to something?
    # Trace    *strings.Builder ## what is this?
    # Warnings []sourceError # informational warnings, shouldn't stop assembly ## use logger
    # Errors   []sourceError # errors that should prevent final assembly ## use logger

    pending: bytearray = attrs.field(factory=bytearray)
    """Running bytes as they are assembled. jumps must be resolved
    and cblocks added before these bytes become a legal program."""

    # intc         []uint64       # observed ints in code. We'll put them into a intcblock
    intc: list[int] = attrs.field(factory=list)
    # intcRefs     []intReference # references to int pseudo-op constants, used for optimization
    intc_refs: list[IntReference] = attrs.field(factory=list)
    # cntIntcBlock int            # prevent prepending intcblock because asm has one
    cnt_intc_block: int = 0
    # hasPseudoInt bool           # were any `int` pseudo ops used?
    has_pseudo_int: bool = False

    # bytec         [][]byte        # observed bytes in code. We'll put them into a bytecblock
    bytec: list[bytes] = attrs.field(factory=list)
    # bytecRefs     []byteReference # references to byte/addr pseudo-op constants, used for optimization
    bytec_refs: list[ByteReference] = attrs.field(factory=list)
    # cntBytecBlock int             # prevent prepending bytecblock because asm has one
    cnt_bytec_block: int = 0
    # hasPseudoByte bool            # were any `byte` (or equivalent) pseudo ops used?
    has_pseudo_byte: bool = False

    # # tracks information we know to be true at the point being assembled
    known: ProgramKnowledge = attrs.field(factory=ProgramKnowledge)
    type_tracking: bool = True

    # # current sourceLine during assembly
    source_line: int = 0

    # # map label string to position within pending buffer
    labels: dict[str, int] = attrs.field(factory=dict)

    # # track references in order to patch in jump offsets
    label_references: list[LabelReference] = attrs.field(factory=list)

    # # map opcode offsets to source location
    offset_to_source: dict[int, TealSourceLocation] = attrs.field(factory=dict)

    has_stateful_ops: bool = False

    # # Need new copy for each opstream
    # versionedPseudoOps map[string]map[int]OpSpec
    versioned_pseudo_ops: dict[str, dict[int, OpSpec]] = attrs.field(factory=dict)

    macros: dict[str, list[Token]] = attrs.field(factory=dict)

    def assemble(self, text: str) -> bytes:
        if (
            self.version is not None
            and self.version not in algo_constants.SUPPORTED_TEAL_LANGUAGE_VERSIONS
        ):
            raise InternalError(f"Can not assemble version {self.version}")
        text = text.strip()
        if not text:
            raise InternalError("Cannot assemble empty program text")
        for line in text.splitlines():
            self.source_line += 1  # why? aren't they supposed to start at zero?
            tokens = tokens_from_line(line, self.source_line)
            if tokens:  # noqa: SIM102
                if (first := tokens[0]).value.startswith("#"):
                    directive = first.value[1:]
                    try:
                        d_func = DIRECTIVES[directive]
                    except KeyError:
                        logger.error(f"Unknown directive: {directive}")  # noqa: TRY400
                    else:
                        d_func(self, tokens)
                    continue
            current, next_ = next_statement(self, tokens)
            while current or next_:
                if not current:
                    continue
                # we're about to begin processing opcodes, so settle the Version
                if self.version is None:
                    self.version = ASSEMBLER_DEFAULT_VERSION
                    self.recheck_macro_names()
                if not self.versioned_pseudo_ops:
                    self.versioned_pseudo_ops = prepare_versioned_pseudo_table(self.version)
                opstring = current[0].value
                if opstring.endswith(":"):
                    label_name = opstring[:-1]
                    if label_name in self.macros:
                        logger.error(f"Cannot create label with same name as macro: {label_name}")
                    else:
                        self.create_label(current[0])
                    current = current[1:]
                    if not current:
                        continue
                    opstring = current[0].value

                spec, expanded_name, ok = get_spec(self, current[0], len(current) - 1)
                if ok:
                    line_, column = current[0].line, current[0].col
                    self.record_source_location(line_, column)
                    if spec.mode == "app":
                        self.has_stateful_ops = True
                    args, returns = spec.arg_types, spec.return_types
                    if spec.refine is not None:
                        nargs, nreturns = spec.refine(self.known, current[1:])
                        if nargs is not None:
                            args = nargs
                        if nreturns is not None:
                            returns = nreturns
                    self.track_stack(args, returns, expanded_name, current)
                    spec.asm(self, current[0], current[1:])
                    if spec.deadens():  # // An unconditional branch deadens the following code
                        self.known.deaden()
                    if spec.name == "callsub":
                        # since retsub comes back to the callsub, it is an entry point like a label
                        self.known.label()

                current, next_ = next_statement(self, next_)
        if self.version and self.version > optimizeConstantsEnabledVersion:
            # TODO: implement
            # self.optimize_intc_block()
            # self.optimize_bytec_block()
            pass
        self.resolve_labels()
        # TODO: errors check?
        return self.prepend_c_blocks()

    # createLabel inserts a label to point to the next instruction, reporting an
    # error for a duplicate.
    def create_label(self, with_colon: Token) -> None:
        label = with_colon.value.removesuffix(":")
        if label in self.labels:
            logger.error(f"duplicate label {label}")
        self.labels[label] = len(self.pending)
        self.known.label()

    def recheck_macro_names(self) -> None:
        raise NotImplementedError

    def record_source_location(self, line: int, column: int) -> None:
        self.offset_to_source[len(self.pending)] = TealSourceLocation(line - 1, column)

    def resolve_labels(self) -> None:
        raw = self.pending.copy()
        reported = set[str]()
        for lr in self.label_references:
            dest = self.labels.get(lr.label.value)
            if dest is None:
                if lr.label.value not in reported:
                    logger.error(f"reference to undefined label {lr.label.value}")
                    reported.add(lr.label.value)
                continue
            # All branch targets are encoded as 2 offset bytes. The destination is relative to the end of the
            # instruction they appear in, which is available in lr.offsetPostion
            jump = dest - lr.offset_position
            if jump > 0x7FFF:
                logger.error(f"label {lr.label.value} is too far away")
                continue
            raw[lr.position] = jump >> 8
            raw[lr.position + 1] = jump & 0x0FF
        self.pending = raw

    def prepend_c_blocks(self) -> bytes:
        # TODO: implement
        return bytes(self.pending)

    def track_stack(
        self,
        args: list[StackType],
        returns: list[StackType],
        instruction: str,
        tokens: list[Token],
    ) -> None:
        # TODO: implement
        pass


# optimizeConstantsEnabledVersion is the first version of TEAL where the
# assembler optimizes constants introduced by pseudo-ops
optimizeConstantsEnabledVersion: typing.Final = 4


@attrs.define
class Token:
    value: str
    col: int
    line: int


DirectiveFunc: typing.TypeAlias = typing.Callable[[OpStream, list[Token]], None]


def pragma(ops: OpStream, tokens: list[Token]) -> None:
    pass


def define(ops: OpStream, tokens: list[Token]) -> None:
    pass


DIRECTIVES = {"pragma": pragma, "define": define}


def next_statement(ops: OpStream, tokens: list[Token]) -> tuple[list[Token], list[Token]]:
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        replacement = ops.macros.get(tok.value)
        if replacement is not None:
            tokens[i : i + 1] = replacement
            # backup to handle potential re-expansion of the first token in the expansion
            i -= 1
            continue
        if tok.value == ";":
            return tokens[:i], tokens[i + 1 :]
        i += 1
    return tokens, []


def get_spec(ops: OpStream, mnemonic: Token, arg_count: int) -> tuple[OpSpec, str, bool]:
    raise NotImplementedError


# newline not included since handled in scanner
TOKEN_SEPARATORS: typing.Final = frozenset(("\t", " ", ";"))


# tokensFromLine splits a line into tokens, ignoring comments. tokens are
# annotated with the provided lineno, and column where they are found.
def tokens_from_line(source_line: str, line_no: int) -> list[Token]:
    tokens = []

    i = 0
    while i < len(source_line) and source_line[i] in TOKEN_SEPARATORS:
        if source_line[i] == ";":
            tokens.append(Token(";", i, line_no))
        i += 1

    start = i
    in_string = False  # tracked to allow spaces and comments inside
    in_base64 = False  # tracked to allow '//' inside
    while i < len(source_line):
        if source_line[i] not in TOKEN_SEPARATORS:  # if not space
            match source_line[i]:
                case '"':  # is a string literal?
                    if not in_string:
                        if i == 0 or i > 0 and source_line[i - 1] in TOKEN_SEPARATORS:
                            in_string = True
                    else:  # noqa: PLR5501
                        if source_line[i - 1] != "\\":  # if not escape symbol
                            in_string = False
                case "/":  # is a comment?
                    if (
                        i < len(source_line) - 1
                        and source_line[i + 1] == "/"
                        and (not in_base64)
                        and (not in_string)
                    ):
                        if start != i:  # if a comment without whitespace
                            tokens.append(Token(source_line[start:i], start, line_no))
                        return tokens
                case "(":  # is base64( seq?
                    prefix = source_line[start:i]
                    if prefix in ("base64", "b64"):
                        in_base64 = True
                case ")":  #  is ) as base64( completion
                    if in_base64:
                        in_base64 = False
            i += 1
            continue

        #  we've hit a space, end last token unless inString
        if not in_string:
            s = source_line[start:i]
            tokens.append(Token(s, start, line_no))
            if source_line[i] == ";":
                tokens.append(Token(";", i, line_no))
            if in_base64:
                in_base64 = False
            elif s in ("base64", "b64"):
                in_base64 = True
        i += 1

        # gobble up consecutive whitespace (but notice semis)
        if not in_string:
            while i < len(source_line) and source_line[i] in TOKEN_SEPARATORS:
                if source_line[i] == ";":
                    tokens.append(Token(";", i, line_no))
                i += 1
            start = i

    # add rest of the string if any
    if start < len(source_line):
        tokens.append(Token(source_line[start:i], start, line_no))
    return tokens
