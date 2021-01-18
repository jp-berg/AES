import pytest
import hashlib
from src.key_expansion import *

rcons = rcon_compute()
sbox = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]


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
    assert g(input, round, rcons) == out


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
    expanded = expand_key(key)
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
