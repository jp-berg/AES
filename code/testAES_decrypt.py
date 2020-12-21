from key_expansion import expand_key
import ctypes
from os.path import join
from os import getcwd

inv_sbox = [82, 9, 106, 213, 48, 54, 165, 56, 191, 64, 163, 158, 129, 243, 215, 251, 124, 227, 57, 130, 155, 47, 255, 135, 52, 142, 67, 68, 196, 222, 233, 203, 84, 123, 148, 50, 166, 194, 35, 61, 238, 76, 149, 11, 66, 250, 195, 78, 8, 46, 161, 102, 40, 217, 36, 178, 118, 91, 162, 73, 109, 139, 209, 37, 114, 248, 246, 100, 134, 104, 152, 22, 212, 164, 92, 204, 93, 101, 182, 146, 108, 112, 72, 80, 253, 237, 185, 218, 94, 21, 70, 87, 167, 141, 157, 132, 144, 216, 171, 0, 140, 188, 211, 10, 247, 228, 88, 5, 184, 179, 69, 6, 208, 44, 30, 143, 202, 63, 15, 2, 193, 175, 189, 3, 1, 19, 138, 107, 58, 145, 17, 65, 79, 103, 220, 234, 151, 242, 207, 206, 240, 180, 230, 115, 150, 172, 116, 34, 231, 173, 53, 133, 226, 249, 55, 232, 28, 117, 223, 110, 71, 241, 26, 113, 29, 41, 197, 137, 111, 183, 98, 14, 170, 24, 190, 27, 252, 86, 62, 75, 198, 210, 121, 32, 154, 219, 192, 254, 120, 205, 90, 244, 31, 221, 168, 51, 136, 7, 199, 49, 177, 18, 16, 89, 39, 128, 236, 95, 96, 81, 127, 169, 25, 181, 74, 13, 45, 229, 122, 159, 147, 201, 156, 239, 160, 224, 59, 77, 174, 42, 245, 176, 200, 235, 187, 60, 131, 83, 153, 97, 23, 43, 4, 126, 186, 119, 214, 38, 225, 105, 20, 99, 85, 33, 12, 125]


aeslib = ctypes.CDLL(join(getcwd(),"libaesdecrypt.so"))



def test_multiply():
    tests = [
        (127, 13, 77),
        (7, 9, 63),
        (65, 11, 253)
    ]
    for test in tests:
        try:
            res = aeslib.multiply(test[0], test[1])
            assert res == test[2]
            print(f"successful for {test[0], test[1]}, was {res} as expected")
        except AssertionError as ae:
            print(f"failed for {test[0], test[1]}, should have been {test[2]} but was {res}")


def test_inverseMixColumns():
    test_block = bytearray.fromhex("fde3bad205e5d0d73547964ef1fe37f1")
    reference = bytearray.fromhex("2d7e86a339d9393ee6570a1101904e16")
    byte_array = ctypes.c_ubyte * len(test_block)
    aeslib.inverseMixColumns(byte_array.from_buffer(test_block))

    try:
        assert test_block == reference
        print("inverse MixColumns test passed")
    except AssertionError as ae:
        print("mixColmns test failed", ae)
        print("mixColumns test C result: ", list(map(hex, test_block)))
        print("reference was: ", list(map(hex, reference)))




def test_addRoundKey():
    test_block = bytearray.fromhex("c89991ee7e0c62a54664efc6c781207e")
    test_block_copy = test_block[:]
    test_key = expand_key("d045ecd109c7c51c044415968635d665")[::-1][:16]
    byte_array = ctypes.c_ubyte * len(test_block)
    byte_array_key = ctypes.c_ubyte * len(test_key)
    aeslib.addRoundKey(byte_array.from_buffer(test_block), byte_array_key.from_buffer(test_key))

    reference = bytearray([])
    for bk, bb in zip(test_key, test_block_copy):
        reference.append(bk ^ bb)

    try:
        assert test_block == reference
        print("addRoundKey test passed")
    except AssertionError as ae:
        print("addRoundKey test failed", ae)
        print("addRoundKey in C results in: ", list(map(hex, test_block)))
        print("addRoundKey in python results in: ", list(map(hex, reference)))


def test_inverseSubBytes():
    test_block = bytearray.fromhex("c89991ee7e0c62a54664efc6c781207e")
    test_block_copy = test_block[:]
    byte_array = ctypes.c_ubyte * len(test_block)
    aeslib.inverseSubBytes(byte_array.from_buffer(test_block))

    reference = bytearray([])
    for byte in test_block_copy:
        reference.append(inv_sbox[byte])

    try:
        assert test_block == reference
        print("inverseSubBytes test passed")
    except AssertionError:
        print("inverseSubBytes test failed")
        print("inverseSubBytes in C results in: ", list(map(hex, test_block)))
        print("inverseSubBytes in python results in: ", list(map(hex, reference)))


def test_inverseShiftRows():
    """test vector from FIPS 197 Appendix C, Round 5.is_row, istart"""

    test_block = bytearray.fromhex("e8dab6901477d4653ff7f5e2e747dd4f")
    reference = bytearray.fromhex("e847f56514dadde23f77b64fe7f7d490")
    byte_array = ctypes.c_ubyte * len(test_block)
    aeslib.inverseShiftRows(byte_array.from_buffer(test_block))

    try:
        assert test_block == reference
        print("inverseShiftRows test passed")
    except AssertionError:
        print("inverseShiftRows test failed")
        print("inverseShiftRows in C results in: ", list(map(hex, test_block)))



def main():
    test_addRoundKey()
    test_inverseSubBytes()
    test_inverseShiftRows()
    test_inverseMixColumns()



if __name__ == '__main__':
    exit(main())
