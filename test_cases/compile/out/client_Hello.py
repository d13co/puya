# This file is auto-generated, do not modify
# flake8: noqa
# fmt: off
import typing

import algopy


class Hello(algopy.arc4.ARC4Client, typing.Protocol):
    @algopy.arc4.abimethod(create='require')
    def create(
        self,
        greeting: algopy.arc4.String,
    ) -> None: ...

    @algopy.arc4.abimethod
    def greet(
        self,
        name: algopy.arc4.String,
    ) -> algopy.arc4.String: ...
