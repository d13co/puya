# This file is auto-generated, do not modify
# flake8: noqa
# fmt: off
import typing

import algopy


class HelloFactory(algopy.arc4.ARC4Client, typing.Protocol):
    @algopy.arc4.abimethod
    def do_some_stuff(
        self,
    ) -> None: ...
