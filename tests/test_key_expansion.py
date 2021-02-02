import pytest
import hashlib
from src.key_expansion import *
from src.AES_generator import gen_sbox

rcons = rcon_compute()
sbox = gen_sbox()

@pytest.mark.parametrize(
    ("input_word", "round", "expected"),
    (
        ("2a6c7605", 1, "52386be5"),
        ("7359f67f", 2, "cf42d28f"),
        ("6d7a883b", 3, "d2c4e23c"),
        ("db0bad00", 4, "3b9563b9"),
        ("11f915bc", 5, "b9596582"),
        ("ca0093fd", 6, "23dc5474"),
    )
)
def test_g(input_word, round, expected):
    input = bytes.fromhex(input_word)
    out = bytes.fromhex(expected)
    assert g(input, round, rcons, sbox) == out


# the key expansion is tested against the md5 hash of the full roundkey bytearray
# this is done for readablility
@pytest.mark.parametrize(
    ("key", "md5_expected"),
    (
        ("2b7e151628aed2a6abf7158809cf4f3c", "f6c1800a7aea3a22a75ae7f7b5811285"),
        ("000102030405060708090a0b0c0d0e0f", "a08a07c755b4006eae2c822e183db54b")
    )
)
def test_expand_key(key, md5_expected):
    expanded = expand_key(key, sbox)
    assert hashlib.md5(expanded).hexdigest() == md5_expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    (
        ("fa9ebf01", "01000000", "fb9ebf01"),
        ("4c39b8a9", "02000000", "4e39b8a9"),
        ("50b66d15", "04000000", "54b66d15"),
        ("e12cfa01", "08000000", "e92cfa01")
    )
)
def test_byte_xor(a, b, expected):
    assert byte_xor(bytes.fromhex(a), bytes.fromhex(b)) == bytes.fromhex(expected)
