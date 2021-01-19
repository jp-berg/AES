import ctypes
from os.path import isfile, join, splitext, expanduser, exists
from os import cpu_count, getcwd, urandom, mkdir
from subprocess import check_output
import hashlib
import binascii
import click
from src.key_expansion import expand_key

chunksize = 2**25 #closish to optimal size, needs to be a multiple of 16

def setup():
    if not exists("lib"):
        mkdir("lib")

    compile_gcc_encrypt = """gcc -O2 -w -shared -fpic -Wl,-soname,AES_encrypt -o lib/libaes_encrypt.so src/AES_encrypt.c -fopenmp""".split()
    compile_clang_encrypt = """clang-O2 -w -shared -fpic -Wl,
                    -soname,AES_encrypt -o ../lib/libaes_encrypt.so src/AES_encrypt.c -fopenmp""".split()

    src_dir = join(getcwd(), "src")
    lib_dir = join(getcwd(), "lib")

    if not isfile(join(lib_dir, "libaes_encrypt.so")):
        if not isfile(join(src_dir, "AES_encrypt.c")):
            raise FileNotFoundError("""No C-library-source-code available.
                                    Please include a 'AES_encrypt.c'-file in the src directory""")
        try:
            o = check_output(compile_gcc_encrypt)
            if o:
                raise RuntimeError("""While compiling AES_encrypt.c
                                   GCC encountered an Error:\n""" + o)
        except FileNotFoundError:
            try:
                o = check_output(compile_clang_encrypt)
                if o:
                    raise RuntimeError("""While compiling AES_encrypt.c
                                       Clang encountered an Error:\n""" + o)
            except FileNotFoundError:
                raise FileNotFoundError("""GCC or Clang not found.
                                        Please install either
                                        or compile AES_encrypt.c to libaes_encrypt.so
                                        on your own.""")
    global aeslib_encrypt
    aeslib_encrypt = ctypes.CDLL(join(lib_dir,"libaes_encrypt.so"))


    compile_gcc_decrypt = """gcc -O2 -w -shared -fpic -Wl,-soname,AES_decrypt -o lib/libaes_decrypt.so src/AES_decrypt.c -fopenmp""".split()

    if not isfile(join(lib_dir, "libaes_decrypt.so")):
        if not isfile(join(src_dir,"AES_decrypt.c")):
            raise FileNotFoundError("""No C-library-source-code available.
                                    Please include a 'AES_decrypt.c'-file in the src directory""")
        try:
            o = check_output(compile_gcc_decrypt)
            if o:
                raise RuntimeError("""While compiling AES_decrypt.c
                                   GCC encountered an Error:\n""" + o)
        except FileNotFoundError as e:
            try:
                o = check_output(compile_clang_encrypt)
                if o:
                    raise RuntimeError("""While compiling AES_decrypt.c
                                       Clang encountered an Error:\n""" + o)
            except FileNotFoundError:
                raise FileNotFoundError("""GCC or Clang not found.
                                        Please install either
                                        or compile AES_decrypt.c to libaes_decrypt.so
                                        on your own.""")
    global aeslib_decrypt
    aeslib_decrypt = ctypes.CDLL(join(lib_dir, "libaes_decrypt.so"))


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


def encrypt(byte_array, keys):
    byte_array = bytearray(byte_array)
    byte_array_keys = ctypes.c_ubyte * len(keys)
    byte_array_file = ctypes.c_ubyte * len(byte_array)
    aeslib_encrypt.encryptBlocks(
        byte_array_file.from_buffer(byte_array),
        byte_array_keys.from_buffer(keys),
        len(byte_array),
        10
    )
    return byte_array

def decrypt(byte_array, keys):
    byte_array = bytearray(byte_array)
    byte_array_keys = ctypes.c_ubyte * len(keys)
    byte_array_file = ctypes.c_ubyte * len(byte_array)
    aeslib_decrypt.decryptBlocks(
        byte_array_file.from_buffer(byte_array),
        byte_array_keys.from_buffer(keys),
        len(byte_array),
        10
    )
    return byte_array

@cli.command("te")
@click.argument("ciphertext")
@click.argument("key")
def encrypt_text(ciphertext, key):
    """enrcypts the input text with the given key using AES-128 """
    cipherinput = bytearray(ciphertext.encode("utf-8"))
    cipherinput = pad_input(cipherinput)
    keys = expand_key(key)
    cipheroutput = encrypt(cipherinput, keys)
    click.echo(cipheroutput.hex())


@cli.command("td")
@click.argument("ciphertext")
@click.argument("key")
def decrypt_text(ciphertext, key):
    """decrypts the input text with the given key using AES-128 """
    cipherinput = bytearray.fromhex(ciphertext)
    keys = expand_key(key)
    cipherinput = decrypt(cipherinput, keys)
    cipheroutput = remove_padding(cipherinput)
    click.echo(cipheroutput.decode("utf-8"))

@cli.command("fe")
@click.argument("filepath_in")
@click.argument("key")
def encrypt_file(filepath_in, key):
    """Encrypts a file with AES.

    The function processes the file from filepath_in in chunks to avoid
    high memory usage (see variable chunksize).

    Args:
        filepath_in: String containing the filepath of the unencrypted file
        key: Bytearray with roundkeys for encryption.
            Must have a length of 11 (rounds) * 16 (bytes) = 176

    Returns:
        None
    """
    keys = expand_key(key)
    b = bytearray(chunksize)
    filepath_out = filepath_in + ".enc" # add new fileending
    with open(filepath_in, "rb") as file_in:
        with open(filepath_out, "wb") as file_out:
            cont = True
            while cont:
                b = file_in.read(chunksize)
                if len(b) < chunksize:
                    b = pad_input(b) #pad last chunk
                    cont = False
                b = encrypt(b, keys)
                file_out.write(b)

@cli.command("fd")
@click.argument("filepath_in")
@click.argument("key")
def decrypt_file(filepath_in, key):
    """Decrpyts a file with AES.

    The function processes the file from filepath_in in chunks to avoid
    high memory usage (see variable chunksize).

    Args:
        filepath_in: String containing the filepath of the encrypted file
        key: Bytearray with roundkeys for encryption.
            Must have a length of 11 (rounds) * 16 (bytes) = 176

    Returns:
        None
    """
    keys = expand_key(key)
    b = bytearray(chunksize)
    filepath_out = splitext(filepath_in)[0] # remove ".enc" fileending
    with open(filepath_in, "rb") as file_in:
        with open(filepath_out, "wb") as file_out:
            cont = True
            while cont:
                b = file_in.read(chunksize)
                if len(b) < chunksize:
                    cont = False
                    b = decrypt(b, keys)
                    b = remove_padding(b) # remove padding from last chunk
                else: 
                    b = decrypt(b, keys)
                file_out.write(b)

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
    setup()
    cli()
