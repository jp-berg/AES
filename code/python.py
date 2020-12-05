import ctypes
import pathlib
from os.path import isfile
import subprocess
from sys import exit

compile_gcc = "gcc -O2 -shared -fpic -Wl,-soname,libtest -o test.so libtest.c".split()
compile_clang = "clang -O2 -shared -fpic -Wl,-soname,libtest -o test.so libtest.c".split()

if not isfile("test.so"):
    if not isfile("libtest.c"):
        raise FileNotFoundError("No C-library-source-code available. Please include a 'libtest.c'-file")
    try:
        print(subprocess.check_output(compile_gcc))
    except FileNotFoundError:
        try:
            print(subprocess.check_output(compile_clang))
        except FileNotFoundError:
            raise FileNotFoundError("GCC or Clang not found. Please install either or compile libtest.c to test.lib on your own.")
            sys.exit(1)

ba = bytearray("12345", 'ascii')
char_array = ctypes.c_ubyte * len(ba)

testlib = ctypes.CDLL("/home/pc/sciebo/Dokumente/Uni/AES/git/AES/code/test.so")
testlib.makestuff(char_array.from_buffer(ba), len(ba))

print(ba)


            
    
    
        
    

