import ctypes
from os.path import isfile, join, splitext, expanduser
from os import cpu_count, getcwd, urandom
from subprocess import check_output
import hashlib
import binascii
from key_expansion import expand_key
import click

compile_gcc = """gcc -O2 -w -shared -fpic -Wl,-soname,AES
                -o libaes.so AES.c -fopenmp""".split()
compile_clang = """clang -O2 -w -shared -fpic -Wl,-soname,AES
                -o libaes.so AES.c -fopenmp""".split()

if not isfile("libaes.so"):
    if not isfile("AES.c"):
        raise FileNotFoundError("""No C-library-source-code available.
                                Please include a 'AES.c'-file""")
    try:
        o = check_output(compile_gcc)
        if o:
            raise RuntimeError("""While compiling AES.c
                               GCC encountered an Error:\n""" + o)
    except FileNotFoundError:
        try:
            o = check_output(compile_clang)
            if o:
                raise RuntimeError("""While compiling AES.c
                               Clang encountered an Error:\n""" + o)
        except FileNotFoundError:
            raise FileNotFoundError("""GCC or Clang not found.
                                    Please install either
                                    or compile AES.c to libaes.so
                                    on your own.""")
aeslib_encrypt = ctypes.CDLL(join(getcwd(),"libaes.so"))


compile_gcc_decrypt = """gcc -O2 -w -shared -fpic -Wl,-soname,AES_decrypt
                -o libaesdecrypt.so AES_decrypt.c -fopenmp""".split()


if not isfile("libaesdecrypt.so"):
    if not isfile("AES_decrypt.c"):
        raise FileNotFoundError("""No C-library-source-code available.
                                Please include a 'AES_decrypt.c'-file""")
    try:
        o = check_output(compile_gcc_decrypt)
    except FileNotFoundError as e:
        pass

aeslib = ctypes.CDLL(join(getcwd(),"libaesdecrypt.so"))


@click.group()
def cli():
    pass


def pad_input(ba):
    """pads bytearray to have a length % 16 = 0"""
    topad = 16 - len(ba) % 16
    padding = bytearray([topad] * topad) # PKCS 5, 7
    return ba + padding


def remove_padding(decrypted):
    # PKCS 5, 7
    padding_amount = decrypted[-1]
    padding = bytearray([padding_amount] * padding_amount)
    if decrypted[-padding_amount:] != padding:
        # no padding
        return decrypted
    else:
        # padding
        return decrypted[:-padding_amount]


@cli.command("encrypt")
@click.argument("ciphertext")
@click.argument("key")
def encrypt_aes(ciphertext, key):
    """enrcypts the input text with the given key using AES-128 """
    toencrypt = bytearray(ciphertext.encode("utf-8"))
    if len(toencrypt)%16 != 0:
        toencrypt = pad_input(toencrypt)
    keys = expand_key(key)
    byte_array_keys = ctypes.c_ubyte * len(keys)
    byte_array_file = ctypes.c_ubyte * len(toencrypt)
    aeslib_encrypt.encryptBlocks(
        byte_array_file.from_buffer(toencrypt),
        byte_array_keys.from_buffer(keys),
        len(toencrypt),
        10
    )
    click.echo(toencrypt.hex())


@cli.command("decrypt")
@click.argument("ciphertext")
@click.argument("key")
def decrypt_aes(ciphertext, key):
    """decrypts the input text with the given key using AES-128 """
    cipherinput = bytearray.fromhex(ciphertext)
    keys = expand_key(key)
    byte_array = ctypes.c_ubyte * len(cipherinput)
    byte_array_keys = ctypes.c_ubyte * len(keys)
    aeslib.decryptBlocks(
        byte_array.from_buffer(cipherinput),
        byte_array_keys.from_buffer(keys),
        len(cipherinput)
    )
    cipheroutput = remove_padding(cipherinput)
    click.echo(cipheroutput.decode("utf-8"))


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


if __name__ == '__main__':
    cli()
