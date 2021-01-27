from time import perf_counter
from os import urandom, getcwd
from os.path import isfile, join, splitext, expanduser
import pytest
import ctypes
import pyaes

from src.key_expansion import expand_key
from src.AES_generator import gen_mult_lookup, gen_sbox


aeslib = ctypes.CDLL(join(getcwd(),"lib","libaes_encrypt.so"))
sbox = gen_sbox()
gal_mult_lookup = gen_mult_lookup()


# Vectors from [FIPS 197] Appendix C, Rounds 1, 2, 3
@pytest.mark.parametrize(
    ("input_block", "expected"),
    (
        ("63cab7040953d051cd60e0e7ba70e18c", "6353e08c0960e104cd70b751bacad0e7"),
        ("a761ca9b97be8b45d8ad1a611fc97369", "a7be1a6997ad739bd8c9ca451f618b61"),
        ("3b59cb73fcd90ee05774222dc067fb68", "3bd92268fc74fb735767cbe0c0590e2d")
    )
)
def test_ShiftRows(input_block, expected):
    """Tests the C-implementation of the ShiftRows-function"""
    ba = bytearray.fromhex(input_block)
    reference = bytearray.fromhex(expected)
    byte_array = ctypes.c_ubyte * len(ba)
    temp_array = ctypes.c_ubyte * len(ba)
    aeslib.ShiftRows(byte_array.from_buffer(ba), temp_array.from_buffer_copy(ba))
    assert ba == reference


# Vectors from [FIPS 197] Appendix C, Rounds 1, 2, 3
@pytest.mark.parametrize(
    ("input_block", "expected"),
    (
        ("6353e08c0960e104cd70b751bacad0e7", "5f72641557f5bc92f7be3b291db9f91a"),
        ("a7be1a6997ad739bd8c9ca451f618b61", "ff87968431d86a51645151fa773ad009"),
        ("3bd92268fc74fb735767cbe0c0590e2d", "4c9c1e66f771f0762c3f868e534df256")
    )
)
def test_MixColumns(input_block, expected):
    """Tests the C-implementation of the MixColumns-function"""
    ba = bytearray.fromhex(input_block)
    reference = bytearray.fromhex(expected)
    byte_array = ctypes.c_ubyte * len(ba)
    temp_array = ctypes.c_ubyte * len(ba)
    gal_mult_lookup_array = ctypes.c_ubyte * len(gal_mult_lookup)
    aeslib.MixColumns(byte_array.from_buffer(ba), temp_array.from_buffer_copy(ba),
                      gal_mult_lookup_array.from_buffer(gal_mult_lookup))
    assert ba == reference


#Vector from [FIPS 197] Appendix B
@pytest.mark.parametrize(
    ("plaintext", "key", "expected"),
    (
        (
            "3243f6a8885a308d313198a2e0370734",
            "2b7e151628aed2a6abf7158809cf4f3c",
            "3925841d02dc09fbdc118597196a0b32"
        ),
    )
)
def test_EncryptBlock(plaintext, key, expected):
    """Tests the C-implementation of the AES-Encryption of a single block"""
    ba = bytearray.fromhex(plaintext)
    byte_array_block = ctypes.c_ubyte * len(ba)

    reference = bytearray.fromhex(expected)
    baKey = expand_key(key)
    byte_array_key = ctypes.c_ubyte * len(baKey)

    temp_array = ctypes.c_ubyte * len(ba)
    sbox_array = ctypes.c_ubyte * len(sbox)
    gal_mult_lookup_array = ctypes.c_ubyte * len(gal_mult_lookup)


    aeslib.encryptBlock(byte_array_block.from_buffer(ba), temp_array.from_buffer_copy(ba),
                        byte_array_key.from_buffer(baKey), 10, sbox_array.from_buffer(sbox),
                        gal_mult_lookup_array.from_buffer(gal_mult_lookup))
    assert ba == reference


def test_EncryptBlockRandom():
    """
    Tests the C-implementation of the AES-Encryption of an arbitrary number of individual blocks.
    Plaintext and Key are randomized each time.
    """
    ba = bytearray(16)
    byte_array_block = ctypes.c_ubyte * len(ba)
    key = bytearray(16)
    baKey = bytearray(176)
    byte_array_key = ctypes.c_ubyte * len(baKey)
    temp_array = ctypes.c_ubyte * len(ba)
    sbox_array = ctypes.c_ubyte * len(sbox)
    gal_mult_lookup_array = ctypes.c_ubyte * len(gal_mult_lookup)
    for i in range(100): #arbitrary number of rounds
        key = urandom(16)
        baKey = expand_key(key.hex())
        b = urandom(16)
        ba = bytearray(b)
        aes_reference = pyaes.AESModeOfOperationECB(key)
        reference = aes_reference.encrypt(b)
        aeslib.encryptBlock(byte_array_block.from_buffer(ba), temp_array.from_buffer_copy(ba),
                        byte_array_key.from_buffer(baKey), 10, sbox_array.from_buffer(sbox),
                        gal_mult_lookup_array.from_buffer(gal_mult_lookup))
        assert ba == reference


@pytest.mark.skip(reason="TODO")
def test_encrypt_file():
    """Tests the C-implementation of the AES-Encryption of a file"""
    toencrypt = "/home/pc/Documents/C.7z"
    password = "aeskurs"
    password = prep_password(password)

    tic = perf_counter()
    file = encrypt_file(toencrypt, password)
    tac = perf_counter() - tic
    print("Time: " + str(tac))


def test_encrypt_aes():
    """Tests the C-implementation of the AES-Encryption on multiple, consecutive, random Blocks.
    """
    no_bytes = 2**15 #arbitrary number of bytes (has to be divisible by 16)
    ba = bytearray(no_bytes)
    byte_array_block = ctypes.c_ubyte * len(ba)
    key = bytearray(16)
    baKey = bytearray(176)
    initvals = bytearray(len(sbox) + len(gal_mult_lookup) + len(baKey))
    byte_array_initvals = ctypes.c_ubyte * len(initvals)
    for i in range(20): #arbitrary number of rounds
        key = urandom(16)
        baKey = expand_key(key.hex())
        initvals = sbox + gal_mult_lookup + baKey
        b = urandom(no_bytes)
        ba = bytearray(b)
        aes_reference = pyaes.AESModeOfOperationECB(key)
        aeslib.encryptAES(byte_array_block.from_buffer(ba),
                        byte_array_initvals.from_buffer(initvals), len(ba), 10)

        i = 0
        while (i < no_bytes):
            current_reference = aes_reference.encrypt(b[i:i+16])
            current_ba = ba[i:i+16]
            assert current_ba == current_reference

            i += 16


if __name__ == '__main__':
    setup()
#[FIPS 197]: FIPS 197, Advanced Encryption Standard
