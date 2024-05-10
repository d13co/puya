# This file is auto-generated, do not modify
# flake8: noqa
# fmt: off
import typing

import algopy


class HelloFactory(algopy.arc4.ARC4Client, typing.Protocol):
    @algopy.arc4.abimethod
    def test_get_program(
        self,
    ) -> None: ...

    @algopy.arc4.abimethod
    def test_abi_call(
        self,
    ) -> None: ...
