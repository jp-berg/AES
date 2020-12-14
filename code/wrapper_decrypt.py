import ctypes
from os.path import isfile, join, splitext, expanduser
from os import cpu_count, getcwd, urandom
from subprocess import check_output
from getpass import getpass
import hashlib
from key_expansion import expand_key

compile_gcc = """gcc -O2 -w -shared -fpic -Wl,-soname,AES_decrypt
                -o libaesdecrypt.so AES_decrypt.c -fopenmp""".split()


if not isfile("libaesdecrypt.so"):
    if not isfile("AES_decrypt.c"):
        raise FileNotFoundError("""No C-library-source-code available.
                                Please include a 'AES_decrypt.c'-file""")
    try:
        o = check_output(compile_gcc)
        if o:
            raise RuntimeError("""While compiling AES_decrypt.c
                               GCC encountered an Error:\n""" + o)
    except FileNotFoundError:
        try:
            o = check_output(compile_clang)
            if o:
                raise RuntimeError("""While compiling AES_decrypt.c
                               Clang encountered an Error:\n""" + o)
        except FileNotFoundError:
            raise FileNotFoundError("""GCC or Clang not found.
                                    Please install either
                                    or compile AES_decrypt.c to libaesdecrypt.so
                                    on your own.""")

aeslib = ctypes.CDLL(join(getcwd(),"libaesdecrypt.so"))
