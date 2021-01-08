import ctypes
from os.path import isfile, join, splitext, expanduser
from os import cpu_count, getcwd, urandom
from subprocess import check_output
from getpass import getpass
import hashlib
from key_expansion import expand_key
import click
import binascii

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


def validate_key(key):
    try:
        # check for valid hex
        int(key, 16)
        # key for Length
        if len(bytearray.fromhex(key)) != 16:
            raise ValueError
        return key
    except ValueError as ve:
        raise click.BadParameter("Key needs to be 16 bytes of valid hexadecimals")


def pad_input(ba):
    """pads bytearray to have a length % 16 = 0"""
    return ba + bytearray(urandom(len(ba) % 16))


@click.command()
@click.option("--text", help="ciphertext", prompt="Text to be decrypted")
@click.option("--key", help="128 bit AES key", prompt="AES-128 Key")
def decrypt(text, key):
    # cipherinput = bytearray(text.encode("utf-8"))
    cipherinput = bytearray.fromhex(text)
    if len(cipherinput)%16 != 0:
        cipherinput = pad_input(cipherinput)
    key = validate_key(key)
    keys = expand_key(key)
    byte_array = ctypes.c_ubyte * len(cipherinput)
    byte_array_keys = ctypes.c_ubyte * len(keys)
    aeslib.decryptBlocks(
        byte_array.from_buffer(cipherinput),
        byte_array_keys.from_buffer(keys),
        len(cipherinput)
    )
    click.echo(binascii.hexlify(cipherinput))

# sdölfkjasödlkfjsdölafjasöldkfjasldkfjaöslkjdf
# cd85acc5d63abae7d4c5c27f543d04e20ee282ad88fd0b028a2cd22c4633d2b7c509471a90b8bf1453e764d427ddb9ff08393bb4
if __name__ == '__main__':
    decrypt()
