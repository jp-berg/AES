import ctypes
from key_expansion import expand_key, format_key_32bit
import pathlib
from os.path import isfile, join, splitext, expanduser
from os import getcwd, cpu_count
import subprocess
from sys import exit
from getpass import getpass
import hashlib
import random
import time




compile_gcc = "gcc -O2 -shared -fpic -Wl,-soname,AES -o libaes.so AES.c -fopenmp".split()
compile_clang = "clang -O2 -shared -fpic -Wl,-soname,AES -o libaes.so AES.c -fopenmp".split()
cpucount = cpu_count()

if not isfile("libaess.so"): #remove s
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

def readFile(filepath):
    b = bytearray(0)
    with open(filepath, "rb") as file:
        f = file.read()
        b = bytearray(f)
    return b

def writeFile(filepath, towrite):
    filepath = splitext(filepath)[0] + ".enc"
    with open(filepath, "wb") as file:
        f = file.write(towrite)
        

def preparePassword(pwd):
    p = hashlib.pbkdf2_hmac(hash_name = 'sha256', password = pwd.encode("utf-8"), salt = "1234".encode("utf-8"), iterations = 10, dklen=16)
    #print("Key: "+ p.hex())
    return expand_key(p.hex())
    
def padBytearray(len_ba):
    
    topad = 16 - len_ba%16
    if not topad:
        topad = 16
    b = [0] * topad
    for i in range(len(b)-1):
        b[i] = random.randrange(0, 255)
    b[topad - 1] = topad
    
    return bytearray(b)

def encryptAES(toencrypt, key):
    toencrypt += padBytearray(len(toencrypt))
    byte_array_key = ctypes.c_ubyte * len(key)
    byte_array_file = ctypes.c_ubyte * len(toencrypt)
    aeslib.encryptAES(byte_array_file.from_buffer(toencrypt), byte_array_key.from_buffer(key), len(toencrypt), cpucount, 10)
    return toencrypt

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

    testkey = "2b7e151628aed2a6abf7158809cf4f3c"
    baKey = expand_key(testkey)
    byte_array_key = ctypes.c_ubyte * len(baKey)
    aeslib.encryptBlock(byte_array_block.from_buffer(baBlock), byte_array_key.from_buffer(baKey), 10)
    print(" ".join(hex(n) for n in baBlock))


def testEncryptAES():
    
##    toencrypt = expanduser(input("Filepath:"))
##    while not isfile(toencrypt):
##        print("Not a file!")
##        toencrypt = expanduser(input("Filepath:"))
##    
##    password  = getpass()
    toencrypt = "/home/pc/Documents/vkt.pdf"
    password = "aeskurs"
    password = preparePassword(password)
    file = readFile(toencrypt)

    tic = time.perf_counter()
    file = encryptAES(file, password)
    tac = time.perf_counter() - tic
    print("Time: " + str(tac))
    writeFile(toencrypt, file)

def gba():
    x = bytearray(16)
    for i in range(16):
        x[i] = random.randrange(0, 255)
    return x

def testEncryptAEStext():
    bl = []
    num = 5
    print("Values: ")
    for i in range(num):
        
        y = gba()
        print(y.hex())
        bl.append(y)
       
    blc = bytearray(0)
    for i in bl:
        blc += i
    key = preparePassword("aeskurs")
    ble = encryptAES(blc, key)
    index = 0
    print("\nEncrypted Values: ")
    s = ble.hex()
    
    while((index + 32)< len(s)):
            print(s[index:index+32])
            index += 32

   
        
            
    
    
        
testEncryptAES()
    
    

    



            
    
    
        
    

