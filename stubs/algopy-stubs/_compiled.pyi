from algopy import Account, Bytes, Contract, LogicSig

def get_logicsig_account(logicsig: LogicSig, /, **template_vars: int | bytes) -> Account:
    """
    Returns the Account for the specified logic signature

    :param logicsig: Logic Signature
    :param template_vars: Template variables to substitute into the logic signature, without the
                          TMPL_ prefix
    """

def get_approval_program(contract: type[Contract], /, **template_vars: int | bytes) -> Bytes:
    """
    Returns the approval program bytes for the specified contract

    :param contract: Contract
    :param template_vars: Template variables to substitute into the logic signature, without the
                          TMPL_ prefix
    """

def get_clear_state_program(contract: type[Contract], /, **template_vars: int | bytes) -> Bytes:
    """
    Returns the clear state program bytes for the specified contract

    :param contract: Contract
    :param template_vars: Template variables to substitute into the logic signature, without the
                          TMPL_ prefix
    """
