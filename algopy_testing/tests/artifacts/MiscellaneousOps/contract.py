from algopy import ARC4Contract, Bytes, UInt64, arc4, op


class MiscellaneousOpsContract(ARC4Contract):
    @arc4.abimethod()
    def verify_addw(self, a: UInt64, b: UInt64) -> tuple[UInt64, UInt64]:
        result = op.addw(a, b)
        return result

    @arc4.abimethod()
    def verify_bytes_bitlen(self, a: Bytes, pad_a_size: UInt64) -> UInt64:
        a = op.bzero(pad_a_size) + a
        result = op.bitlen(a)
        return result

    @arc4.abimethod()
    def verify_uint64_bitlen(self, a: UInt64) -> UInt64:
        result = op.bitlen(a)
        return result

    @arc4.abimethod()
    def verify_sqrt(self, a: UInt64) -> UInt64:
        result = op.sqrt(a)
        return result

    @arc4.abimethod()
    def verify_concat(self, a: Bytes, b: Bytes, pad_a_size: UInt64, pad_b_size: UInt64) -> Bytes:
        a = op.bzero(pad_a_size) + a
        b = op.bzero(pad_b_size) + b
        result = a + b
        result = op.sha256(result)
        return result
