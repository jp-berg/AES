from time import perf_counter
import wrapper
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


def testEncryptAES():
    """Tests the C-implementation of the AES-Encryption of a file"""
    toencrypt = "/home/pc/Documents/vkt.pdf"
    password = "aeskurs"
    password = preparePassword(password)
    file = readFile(toencrypt)

    tic = perf_counter()
    file = encryptAES(file, password)
    tac = perf_counter() - tic
    print("Time: " + str(tac))

    writeFile(toencrypt, file)


def testEncryptAEStext():
    """Tests the C-implementation of the AES-Encryption of multiple blocks"""
    bl = []
    num = 5 # number of blocks
    print("Values: ")
    for i in range(num):
        y = urandom(16)
        print(y.hex()) #prints a block before encryption
        bl.append(y)   
    blc = bytearray(0)
    for i in bl:
        blc += i
    key = preparePassword("aeskurs")
    ble = encryptAES(blc, key)
    index = 0
    print("\nEncrypted Values: ")
    s = ble.hex()
    #Prints one block per line:
    while((index + 32) < len(s)):
            print(s[index:index + 32])
            index += 32

#[FIPS 197]: FIPS 197, Advanced Encryption Standard
