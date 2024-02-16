from puyapy import Contract, arc4, op


class MyContract(Contract):
    def approval_program(self) -> bool:
        # When creating an address from an account no need to check the length as we assume the
        # Account is valid
        sender_address = arc4.Address(op.Transaction.sender)
        # When creating an address from bytes, we check the length is 32 as we don't know the
        # source of the bytes
        checked_address = arc4.Address(op.Transaction.sender.bytes)
        # When using from_bytes, no validation is performed as per all implementations of
        # from_bytes
        unchecked_address = arc4.Address.from_bytes(op.Transaction.sender.bytes)
        assert sender_address == checked_address and checked_address == unchecked_address

        return True

    def clear_state_program(self) -> bool:
        return True