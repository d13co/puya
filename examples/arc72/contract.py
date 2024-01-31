import typing

from puyapy import UInt64, Bytes, arc4, Box, subroutine, BigUInt, Global, bzero, Transaction, err


Bytes256: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[256]]
TokenID: typing.TypeAlias = arc4.UInt256


class Token(arc4.Struct):
    owner: arc4.Address
    uri: Bytes256
    controller: arc4.Address


class Control(arc4.Struct):
    owner: arc4.Address
    controller: arc4.Address


class ARC72Contract(arc4.ARC4Contract):
    def __init__(self) -> None:
        self.next_index = BigUInt(0)

    @subroutine
    def _get_token(self, token_id: TokenID) -> Token:
        data, exists = Box.get(token_id.bytes)
        if not exists:
            # TODO: check this is returning an address
            zero_address_bytes = Global.zero_address().bytes
            return Token(
                owner=arc4.Address.from_bytes(zero_address_bytes),
                controller=arc4.Address.from_bytes(zero_address_bytes),
                uri=Bytes256.from_bytes(bzero(256)),
            )
        return Token.from_bytes(data)

    @subroutine
    def _set_token(self, token_id: TokenID, token: Token) -> None:
        Box.put(token_id.bytes, token.bytes)

    @arc4.abimethod
    def arc72_ownerOf(self, token_id: TokenID) -> arc4.Address:
        return self._get_token(token_id).owner

    @arc4.abimethod
    def arc72_transferFrom(
        self, from_address: arc4.Address, to_address: arc4.Address, token_id: TokenID
    ) -> None:
        token = self._get_token(token_id)
        assert token.owner == from_address, "From address must match owner"

        sender_address = arc4.Address.from_bytes(Transaction.sender().bytes)
        key = Control(
            owner=from_address,
            controller=sender_address,
        )
        (_data, controller_exists) = Box.get(key.bytes)

        if (
            sender_address == from_address
            or token.controller == sender_address
            or controller_exists
        ):
            token.owner = to_address.copy()
            self._set_token(token_id, token.copy())
        else:
            # TODO: Handle this as per spec
            err()

    @arc4.abimethod
    def arc72_tokenURI(self, token_id: TokenID) -> Bytes256:
        return self._get_token(token_id).uri

    @arc4.abimethod
    def arc72_approve(self, operator: arc4.Address, token_id: TokenID) -> None:
        # TODO: Permisions?? who can call this
        token = self._get_token(token_id)
        token.controller = operator.copy()
        self._set_token(token_id, token.copy())

    @arc4.abimethod
    def mint(self, to: arc4.Address) -> None:
        token_id = TokenID(self.next_index)
        zero_address_bytes = Global.zero_address().bytes

        token = Token(
            owner=to.copy(),
            uri=Bytes256.from_bytes(bzero(256)),
            controller=arc4.Address.from_bytes(zero_address_bytes),
        )
        self._set_token(token_id, token.copy())
        self.next_index += 1

    @arc4.abimethod
    def arc72_setApprovalForAll(self, operator: arc4.Address, approved: bool) -> None:
        sender_address = arc4.Address.from_bytes(Transaction.sender().bytes)
        key = Control(
            owner=sender_address,
            controller=operator,
        ).bytes
        if approved:
            Box.put(key, Bytes())
        else:
            Box.delete(key)

    @arc4.abimethod(readonly=True)
    def arc72_totalSupply(self) -> arc4.UInt256:
        return arc4.UInt256(self.next_index)

    @arc4.abimethod(readonly=True)
    def arc72_tokenByIndex(self, index: arc4.UInt256) -> TokenID:
        # TODO: Should this check the index is actually used?
        return index
