from hashlib import sha256
from pathlib import Path

import algokit_utils
import pytest
from algokit_utils import ApplicationClient, get_localnet_default_account
from algokit_utils.config import config
from algopy import UInt64, op
from algopy.primitives.bytes import Bytes
from algopy_testing.constants import MAX_BYTES_SIZE, MAX_UINT64, MAX_UINT512
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from tests.common import AVMInvoker, create_avm_invoker

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
APP_SPEC = ARTIFACTS_DIR / "MiscellaneousOps" / "data" / "MiscellaneousOpsContract.arc32.json"


@pytest.fixture(scope="session")
def ops_client(algod_client: AlgodClient, indexer_client: IndexerClient) -> ApplicationClient:
    config.configure(
        debug=True,
    )

    client = ApplicationClient(
        algod_client,
        APP_SPEC,
        creator=get_localnet_default_account(algod_client),
        indexer_client=indexer_client,
    )

    client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )

    return client


@pytest.fixture(scope="module")
def get_ops_avm_result(
    ops_client: ApplicationClient,
) -> AVMInvoker:
    return create_avm_invoker(ops_client)


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (0, 0),
        (0, MAX_UINT64),
        (MAX_UINT64, 0),
        (1, 0),
        (0, 1),
        (100, 42),
        (1, MAX_UINT64 - 1),
        (MAX_UINT64 - 1, 1),
        (100, MAX_UINT64),
        (MAX_UINT64, MAX_UINT64),
    ],
)
def test_addw(get_ops_avm_result: AVMInvoker, a: int, b: int) -> None:
    avm_result = get_ops_avm_result("verify_addw", a=a, b=b)
    avm_result_tuples = _bytes_to_uint64_tuple(avm_result)
    result = op.addw(UInt64(a), UInt64(b))
    assert avm_result_tuples == result


@pytest.mark.parametrize(
    ("a", "pad_a_size"),
    [
        (int_to_bytes(0), 0),
        (int_to_bytes(1), 0),
        (int_to_bytes(MAX_UINT64), 0),
        (int_to_bytes(MAX_UINT512), 0),
        (int_to_bytes(MAX_UINT512 * MAX_UINT512), 0),
        (b"\x00" * 8 + b"\x0f" * 4, 0),
        (b"\x0f", MAX_BYTES_SIZE - 1),
    ],
)
def test_bytes_bitlen(get_ops_avm_result: AVMInvoker, a: bytes, pad_a_size: int) -> None:
    avm_result = get_ops_avm_result("verify_bytes_bitlen", a=a, pad_a_size=pad_a_size)
    result = op.bitlen(a)
    assert avm_result == result


@pytest.mark.parametrize(
    "a",
    [
        0,
        1,
        42,
        MAX_UINT64,
    ],
)
def test_uint64_bitlen(get_ops_avm_result: AVMInvoker, a: int) -> None:
    avm_result = get_ops_avm_result("verify_uint64_bitlen", a=a)
    result = op.bitlen(a)
    assert avm_result == result


@pytest.mark.parametrize(
    "a",
    [
        0,
        1,
        2,
        9,
        13,
        MAX_UINT64,
    ],
)
def test_sqrt(get_ops_avm_result: AVMInvoker, a: int) -> None:
    avm_result = get_ops_avm_result("verify_sqrt", a=a)
    assert avm_result == op.sqrt(UInt64(a))


@pytest.mark.parametrize(
    ("a", "b", "pad_a_size", "pad_b_size"),
    [
        (b"", b"", 0, 0),
        (b"1", b"", 0, 0),
        (b"", b"1", 0, 0),
        (b"1", b"1", 0, 0),
        (b"", b"0", 0, MAX_BYTES_SIZE - 1),
        (b"0", b"", MAX_BYTES_SIZE - 1, 0),
        (b"1", b"0", 0, MAX_BYTES_SIZE - 2),
        (b"1", b"0", MAX_BYTES_SIZE - 2, 0),
    ],
)
def test_concat(
    get_ops_avm_result: AVMInvoker, a: bytes, b: bytes, pad_a_size: int, pad_b_size: int
) -> None:
    avm_result = get_ops_avm_result(
        "verify_concat", a=a, b=b, pad_a_size=pad_a_size, pad_b_size=pad_b_size
    )
    a = (b"\x00" * pad_a_size) + a
    b = (b"\x00" * pad_b_size) + b
    assert avm_result == get_sha256_hash(op.concat(a, b))


def get_sha256_hash(v: Bytes) -> Bytes:
    return Bytes(sha256(v.value).digest())


def _bytes_to_uint64_tuple(x: object) -> tuple[UInt64, UInt64] | None:
    return (UInt64(x[0]), UInt64(x[1])) if (isinstance(x, bytes | tuple | list)) else None
