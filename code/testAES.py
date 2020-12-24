from time import perf_counter
from os import urandom
from wrapper import prep_password, encrypt_aes, encrypt_file
import key_expansion


def testShiftRows():
    """Tests the C-implementation of the ShiftRows-function"""
    #Vector from [FIPS 197] Appendix B, Round 1, After SubBytes:
    ba = bytearray.fromhex(
        'd4 27 11 ae e0 bf 98 f1 b8 b4 5d e5 1e 41 52 30')
    byte_array = ctypes.c_ubyte * len(ba)
    aeslib.ShiftRows(byte_array.from_buffer(ba), len(ba))
    print(" ".join(hex(n) for n in ba))


def testMixColumns():
    """Tests the C-implementation of the MixColumns-function"""
    #Vector from [FIPS 197] Appendix B, Round 1, After ShiftRows:
    ba = bytearray.fromhex(
        'd4 bf 5d 30 e0 b4 52 ae b8 41 11 f1 1e 27 98 e5')
    byte_array = ctypes.c_ubyte * len(ba)
    aeslib.MixColumns(byte_array.from_buffer(ba), len(ba))
    print(" ".join(hex(n) for n in ba))


def testEncryptBlock():
    """Tests the C-implementation of the AES-Encryption of a single block"""
    #Vector from [FIPS 197] Appendix B, Input:
    baBlock = bytearray.fromhex(
        '32 43 f6 a8 88 5a 30 8d 31 31 98 a2 e0 37 07 34')
    byte_array_block = ctypes.c_ubyte * len(baBlock)

    #Vector from [FIPS 197] Appendix B, Cipher Key:
    testkey = "2b7e151628aed2a6abf7158809cf4f3c"
    baKey = expand_key(testkey)
    byte_array_key = ctypes.c_ubyte * len(baKey)

    aeslib.encryptBlock(byte_array_block.from_buffer(baBlock),
                        byte_array_key.from_buffer(baKey), 10)
    print(" ".join(hex(n) for n in baBlock))


def test_encrypt_file():
    """Tests the C-implementation of the AES-Encryption of a file"""
    toencrypt = "/home/pc/Documents/vkt.pdf"
    password = "aeskurs"
    password = prep_password(password)

    tic = perf_counter()
    file = encrypt_file(toencrypt, password)
    tac = perf_counter() - tic
    print("Time: " + str(tac))


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
test_encrypt_file()

#[FIPS 197]: FIPS 197, Advanced Encryption Standard
