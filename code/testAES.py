from time import perf_counter
from os import urandom, getcwd
from os.path import isfile, join, splitext, expanduser
from wrapper import prep_password, encrypt_aes, encrypt_file
import pytest
import ctypes
from key_expansion import expand_key

aeslib = ctypes.CDLL(join(getcwd(),"libaes.so"))


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
    aeslib.ShiftRows(byte_array.from_buffer(ba), len(ba))
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
    aeslib.MixColumns(byte_array.from_buffer(ba), len(ba))
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

    aeslib.encryptBlock(byte_array_block.from_buffer(ba),
                        byte_array_key.from_buffer(baKey), 10)
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


@pytest.mark.skip(reason="TODO")
def test_encrypt_aes():
    """Tests the C-implementation of the AES-Encryption of multiple blocks.
    Compare with https://www.hanewin.net/encrypt/aes/aes-test.htm
    """
    b = bytearray(0)
    num = 100 # number of blocks
    print("Blocks: ")
    for i in range(num):
        y = bytearray(urandom(16))
        print(str(i) + ": " + y.hex()) #prints a block before encryption
        b += y
    key = prep_password("aeskurs")
    print("\nKey: " + key.hex()[0:32])
    b = encrypt_aes(b, key)
    index = 0
    nr = 0
    print("\nEncrypted Blocks: ")
    s = b.hex()
    #Prints one block per line:
    while((index + 32) <= len(s)):
            print(str(nr) + ": " + s[index:index + 32])
            index += 32
            nr += 1


#[FIPS 197]: FIPS 197, Advanced Encryption Standard
