from src.key_expansion import expand_key
import ctypes
from os.path import join
from os import getcwd
import pytest
import filecmp

from wrapper import *
from src.AES_generator import gen_inverse_sbox, gen_sbox

aeslib = ctypes.CDLL(join(getcwd(),"lib", "libaes_decrypt.so"))
inv_sbox = gen_inverse_sbox()
sbox = gen_sbox()


@pytest.mark.parametrize(
    ('factor_x', 'factor_y', 'expected'),
    (
        (127, 13, 77),
        (7, 9, 63),
        (65, 11, 253),
    )
)
def test_multiply(factor_x, factor_y, expected):
    res = aeslib.multiply(factor_x, factor_y)
    assert res == expected


# Test vectors from rounds 2, 3, 4 of the equivalent inverse cipher
# FIPS 197 Appendix C
@pytest.mark.parametrize(
    ('input_block', 'expected'),
    (
        ("fde3bad205e5d0d73547964ef1fe37f1", "2d7e86a339d9393ee6570a1101904e16"),
        ("d1876c0f79c4300ab45594add66ff41f","39daee38f4f1a82aaf432410c36d45b9"),
        ("c62fe109f75eedc3cc79395d84f9cf5d", "9a39bf1d05b20a3a476a0bf79fe51184"),
    )
)
def test_inverseMixColumns(input_block, expected):
    test_block = bytearray.fromhex(input_block)
    reference = bytearray.fromhex(expected)
    byte_array = ctypes.c_ubyte * len(test_block)
    aeslib.inverseMixColumns(byte_array.from_buffer(test_block))
    assert test_block == reference


# Test vectors from rounds 2, 3, 4 of the inverse cipther
# FIPS 197 Appendix C
@pytest.mark.parametrize(
    ('input_block', 'round_key', 'expected'),
    (
        (
            "fde3bad205e5d0d73547964ef1fe37f1",
            "47438735a41c65b9e016baf4aebf7ad2",
            "baa03de7a1f9b56ed5512cba5f414d23"
        ),
        (
            "d1876c0f79c4300ab45594add66ff41f",
            "14f9701ae35fe28c440adf4d4ea9c026",
            "c57e1c159a9bd286f05f4be098c63439"
        ),
        (
            "c62fe109f75eedc3cc79395d84f9cf5d",
            "5e390f7df7a69296a7553dc10aa31f6b",
            "9816ee7400f87f556b2c049c8e5ad036"
        ),
    )
)
def test_addRoundKey(input_block, round_key, expected):
    test_block = bytearray.fromhex(input_block)
    reference = bytearray.fromhex(round_key)
    test_key = bytearray.fromhex(expected)
    byte_array = ctypes.c_ubyte * len(test_block)
    byte_array_key = ctypes.c_ubyte * len(test_key)
    aeslib.addRoundKey(
        byte_array.from_buffer(test_block),
        byte_array_key.from_buffer(test_key)
    )
    assert test_block == reference


# Test vectors from rounds 2, 3, 4 of the equivalent inverse cipher
# FIPS 197 Appendix C
@pytest.mark.parametrize(
    ('input_block', 'expected'),
    (
        ("54d990a16ba09ab596bbf40ea111702f", "fde596f1054737d235febad7f1e3d04e"),
        ("3e1c22c0b6fcbf768da85067f6170495", "d1c4941f7955f40fb46f6c0ad68730ad"),
        ("b458124c68b68a014b99f82e5f15554c", "c65e395df779cf09ccf9e1c3842fed5d")
    )
)
def test_inverseSubBytes(input_block, expected):
    test_block = bytearray.fromhex(input_block)
    reference = bytearray.fromhex(expected)
    byte_array = ctypes.c_ubyte * len(test_block)
    byte_array_inv_sbox = ctypes.c_ubyte * 256
    aeslib.inverseSubBytes(
        byte_array.from_buffer(test_block),
        byte_array_inv_sbox.from_buffer(inv_sbox)
    )
    assert test_block == reference


# Test vectors from rounds 2, 3, 4 of the equivalent inverse cipher
# FIPS 197 Appendix C
@pytest.mark.parametrize(
    ('input_block', 'expected'),
    (
        ("fde596f1054737d235febad7f1e3d04e", "fde3bad205e5d0d73547964ef1fe37f1"),
        ("d1c4941f7955f40fb46f6c0ad68730ad", "d1876c0f79c4300ab45594add66ff41f"),
        ("c65e395df779cf09ccf9e1c3842fed5d", "c62fe109f75eedc3cc79395d84f9cf5d")
    )
)
def test_inverseShiftRows(input_block, expected):
    """test vector from FIPS 197 Appendix C, Round 5.is_row, istart"""
    test_block = bytearray.fromhex(input_block)
    reference = bytearray.fromhex(expected)
    byte_array = ctypes.c_ubyte * len(test_block)
    aeslib.inverseShiftRows(byte_array.from_buffer(test_block))
    assert test_block == reference


@pytest.mark.parametrize(
    ('input_block', 'key', 'expected'),
    (
        (
            "69c4e0d86a7b0430d8cdb78070b4c55a",
            "000102030405060708090a0b0c0d0e0f",
            "00112233445566778899aabbccddeeff"
        ),
    )
)
def test_decryptBlock(input_block, key, expected):
    test_block = bytearray.fromhex(input_block)
    reference = bytearray.fromhex(expected)
    keys = expand_key(key, sbox)
    byte_array = ctypes.c_ubyte * len(test_block)
    byte_array_keys = ctypes.c_ubyte * len(keys)
    byte_array_inv_sbox = ctypes.c_ubyte * 256
    aeslib.decryptBlock(
        byte_array.from_buffer(test_block),
        byte_array_keys.from_buffer(keys),
        byte_array_inv_sbox.from_buffer(inv_sbox)
    )
    assert test_block == reference



def test_decrypt_file():
        filepath_in = join(getcwd(), "tests", "files", "encrypted.enc")
        key = "f" * 32
        keys = prep_password(key, 0)
        chunksize = 2**25
        b = bytearray(chunksize)
        filepath_out = filepath_in.split(".")[0]
        with open(filepath_in, "rb") as file_in:
            with open(filepath_out, "wb") as file_out:
                cont = True
                while cont:
                    b = file_in.read(chunksize)
                    if len(b) < chunksize:
                        cont = False
                        b = decrypt(b, keys)
                        b = remove_padding(b) # remove padding from last chunk
                    else:
                        b = decrypt(b, keys)
                    file_out.write(b)

        compare = join(getcwd(), "tests", "files", "plain")
        assert filecmp.cmp(filepath_out, compare)
