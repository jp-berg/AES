import ctypes
import pathlib
from os.path import isfile, join
from os import getcwd
import subprocess
from sys import exit


compile_gcc = "gcc -O2 -shared -fpic -Wl,-soname,AES -o libaes.so AES.c".split()
compile_clang = "clang -O2 -shared -fpic -Wl,-soname,AES -o libaes.so AES.c".split()

if not isfile("libaes.so"):
    if not isfile("AES.c"):
        raise FileNotFoundError("No C-library-source-code available. Please include a 'libtest.c'-file")
    try:
        print(subprocess.check_output(compile_gcc))
    except FileNotFoundError:
        try:
            print(subprocess.check_output(compile_clang))
        except FileNotFoundError:
            raise FileNotFoundError("GCC or Clang not found. Please install either or compile libtest.c to test.lib on your own.")
            sys.exit(1)
    
aeslib = ctypes.CDLL(join(getcwd(),"libaes.so"))

def testShiftRows():
    ba = bytearray.fromhex('d4 27 11 ae e0 bf 98 f1 b8 b4 5d e5 1e 41 52 30')
    byte_array = ctypes.c_ubyte * len(ba)

    aeslib.ShiftRows(byte_array.from_buffer(ba), len(ba))
    print(" ".join(hex(n) for n in ba))

def testMixColumns():
    ba = bytearray.fromhex('d4 bf 5d 30 e0 b4 52 ae b8 41 11 f1 1e 27 98 e5')
    byte_array = ctypes.c_ubyte * len(ba)

    aeslib.MixColumns(byte_array.from_buffer(ba), len(ba))
    print(" ".join(hex(n) for n in ba))

def testSubBytes():
    pass

def testAddKeyRound():
    pass

def testEncryptBlock():
    baBlock = bytearray.fromhex('32 43 f6 a8 88 5a 30 8d 31 31 98 a2 e0 37 07 34')
    byte_array_block = ctypes.c_ubyte * len(baBlock)
    baKey = bytearray.fromhex('2b 7e 15 16 28 ae d2 a6 ab f7 15 88 09 cf 4f 3c')
    byte_array_key = ctypes.c_ubyte * len(baBlock)
   
    aeslib.encryptBlock(byte_array_block.from_buffer(baBlock), byte_array_key.from_buffer(baKey), 10)
    print(" ".join(hex(n) for n in baBlock))


testMixColumns()

            
    
    
        
    

