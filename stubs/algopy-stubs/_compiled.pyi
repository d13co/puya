from algopy import Account, Bytes, Contract, LogicSig

def get_logicsig_account(
    logicsig: LogicSig, /, prefix: str = ..., **template_vars: int | bytes
) -> Account:
    """
    Returns the Account for the specified logic signature

    :param logicsig: Logic Signature
    :param prefix: Prefix to add to provided template vars,
                   defaults to the prefix supplied on command line
    :param template_vars: Template variables to substitute into the logic signature,
                          without the prefix
    """

def get_approval_program(
    contract: type[Contract], /, prefix: str = ..., **template_vars: int | bytes
) -> Bytes:
    """
    Returns the approval program bytes for the specified contract

    :param contract: Contract
    :param prefix: Prefix to add to provided template vars,
                   defaults to the prefix supplied on command line
    :param template_vars: Template variables to substitute into the logic signature,
                          without the prefix
    """

def get_clear_state_program(
    contract: type[Contract], /, prefix: str = ..., **template_vars: int | bytes
) -> Bytes:
    """
    Returns the clear state program bytes for the specified contract

    :param contract: Contract
    :param prefix: Prefix to add to provided template vars,
                   defaults to the prefix supplied on command line
    :param template_vars: Template variables to substitute into the logic signature,
                          without the prefix
    """
