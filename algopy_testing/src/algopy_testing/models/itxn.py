from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict, TypeVar

if TYPE_CHECKING:
    # from algopy_testing.models.asset import Asset
    import algopy

T = TypeVar("T")


class ITxnFields(TypedDict, total=False):
    sender: algopy.Account
    fee: algopy.UInt64
    first_valid: algopy.UInt64
    last_valid: algopy.UInt64
    note: algopy.Bytes
    lease: algopy.Bytes
    receiver: algopy.Account
    amount: algopy.UInt64
    close_remainder_to: algopy.Account
    vote_pk: algopy.Bytes
    selection_pk: algopy.Bytes
    vote_first: algopy.UInt64
    vote_last: algopy.UInt64
    vote_key_dilution: algopy.UInt64
    type: algopy.Bytes
    type_enum: algopy.UInt64
    xfer_asset: algopy.Asset
    asset_amount: algopy.UInt64
    asset_sender: algopy.Account
    asset_receiver: algopy.Account
    asset_close_to: algopy.Account
    group_index: algopy.UInt64
    tx_id: algopy.Bytes
    application_id: algopy.Application
    on_completion: algopy.UInt64
    approval_program: algopy.Bytes
    clear_state_program: algopy.Bytes
    rekey_to: algopy.Account
    config_asset: algopy.Asset
    config_asset_total: algopy.UInt64
    config_asset_decimals: algopy.UInt64
    config_asset_default_frozen: bool
    config_asset_unit_name: algopy.Bytes
    config_asset_name: algopy.Bytes
    config_asset_url: algopy.Bytes
    config_asset_metadata_hash: algopy.Bytes
    config_asset_manager: algopy.Account
    config_asset_reserve: algopy.Account
    config_asset_freeze: algopy.Account
    config_asset_clawback: algopy.Account
    freeze_asset: algopy.Asset
    freeze_asset_account: algopy.Account
    freeze_asset_frozen: bool
    global_num_uint: algopy.UInt64
    global_num_byte_slice: algopy.UInt64
    local_num_uint: algopy.UInt64
    local_num_byte_slice: algopy.UInt64
    extra_program_pages: algopy.UInt64
    nonparticipation: bool
    created_asset_id: algopy.Asset
    created_application_id: algopy.Application
    last_log: algopy.Bytes
    state_proof_pk: algopy.Bytes


@dataclass
class _ITxn:
    def __getattr__(self, name: str) -> object:
        from algopy_testing.context import get_test_context

        context = get_test_context()
        if not context:
            raise ValueError(
                "Test context is not initialized! Use `with algopy_testing_context()` to access "
                "the context manager."
            )
        if not context.itxn_fields:
            raise ValueError(
                "`algopy.ITxn` fields are not set in the test context! "
                "Use `context.patch_itxn_fields()` to set the fields in your test setup."
            )
        if name not in context.itxn_fields:
            raise AttributeError(
                f"'Txn' object has no value set for attribute named '{name}'. "
                f"Use `context.patch_itxn_fields({name}=your_value)` to set the value "
                "in your test setup."
            )
        if not context.itxn_fields[name]:
            raise TypeError(
                f"The value for '{name}' in the test context is None. "
                f"Make sure to patch the global field '{name}' using your `AlgopyTestContext` "
                "instance."
            )

        return context.itxn_fields[name]


ITxn = _ITxn()