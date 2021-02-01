import ctypes
from os.path import isfile, join, splitext, expanduser, exists
from os import cpu_count, getcwd, urandom, mkdir
from subprocess import check_output
import hashlib
import binascii
import click
from src.key_expansion import expand_key
from src.AES_generator import gen_mult_lookup, gen_sbox, gen_inverse_sbox


cpucount = cpu_count()
sbox = gen_sbox()
inv_sbox = gen_inverse_sbox()
mult_lookup = gen_mult_lookup()


def setup():
    if not exists("lib"):
        mkdir("lib")

    compile_gcc_encrypt = """gcc -O2 -w -shared -fpic -fstrict-aliasing -Wl,-soname,AES_encrypt -o lib/libaes_encrypt.so src/AES_encrypt.c -fopenmp""".split()
    compile_clang_encrypt = """clang-O2 -w -shared -fpic -fstrict-aliasing -Wl,
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


    compile_gcc_decrypt = """gcc -O2 -w -shared -fpic -Wl,-soname,AES_decrypt -o lib/libaes_decrypt.so src/AES_decrypt.c""".split()
    compile_clang_decrypt = """clang -O2 -w -shared -fpic -Wl,-soname,AES_decrypt -o lib/libaes_decrypt.so src/AES_decrypt.c""".split()

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
    """Function to capture all cli components into a group"""
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


def validate_chunksize(ctx, param, chunksize):
    try:
        if chunksize % 16 != 0:
            raise ValueError
        return chunksize
    except ValueError as e:
        raise click.BadParameter("chunksize needs to be a multiple of 16")




def prep_password(key, iterations):
    """
    Generates bytearray containing the consecutive
    round keys from an arbitrary string.
    """
    if iterations != 0:
        #Use higher iteration values (>3000000) for more security:
        key = hashlib.pbkdf2_hmac(hash_name = 'sha256',
                                password = key.encode("utf-8"),
                                salt = "aeskurs".encode("utf-8"), #TODO: change salt
                                iterations = iterations, dklen = 16).hex()
    else:
        validate_key(key)
    return expand_key(key, sbox)


def encrypt(byte_array, keys):
    initvals = sbox + mult_lookup + keys
    byte_array = bytearray(byte_array)
    byte_array_initvals = ctypes.c_ubyte * len(initvals)
    byte_array_file = ctypes.c_ubyte * len(byte_array)
    aeslib_encrypt.encryptAES(
        byte_array_file.from_buffer(byte_array),
        byte_array_initvals.from_buffer(initvals),
        len(byte_array),
        10
    )
    return byte_array


def decrypt(byte_array, keys):
    byte_array = bytearray(byte_array)
    byte_array_keys = ctypes.c_ubyte * len(keys)
    byte_array_file = ctypes.c_ubyte * len(byte_array)
    byte_array_inv_sbox = ctypes.c_ubyte * 256
    aeslib_decrypt.decryptBlocks(
        byte_array_file.from_buffer(byte_array),
        byte_array_keys.from_buffer(keys),
        len(byte_array),
        byte_array_inv_sbox.from_buffer(inv_sbox)
    )
    return byte_array


@cli.command("te")
@click.argument("password")
@click.argument("ciphertext")
@click.option(
    "-k",
    "--key",
    default=False,
    is_flag=True,
    help="use 16-byte hexadecimal key instead of password of arbitrary length"
)
@click.option(
    "-h",
    "--hex",
    default=False,
    is_flag=True,
    help="interpret the input as pure unencoded hexadecimal bytes"
)
def encrypt_text(password, ciphertext, key, hex):
    """Enrcypts the input text with the given key using AES-128. """
    iterations = 0 if key else 200000
    keys = prep_password(password, iterations)
    if hex:
        try:
            cipherinput = bytearray.fromhex(ciphertext)
        except ValueError as ve:
            raise click.BadParameter("Input needs to complete bytes in valid hexadecimal")
        # explicit padding here, so single blocks work as intented
        if len(cipherinput) > 16:
            cipherinput = pad_input(cipherinput)
        cipheroutput = encrypt(cipherinput, keys)
    else:
        cipherinput = bytearray(ciphertext.encode("utf-8"))
        padded = pad_input(cipherinput)
        cipheroutput = encrypt(padded, keys)
    click.echo(cipheroutput.hex())




@cli.command("td")
@click.argument("password")
@click.argument("ciphertext")
@click.option(
    "-k",
    "--key",
    default=False,
    is_flag=True,
    help="use 16-byte hexadecimal key instead of password of arbitrary length"
)
@click.option(
    "-h",
    "--hex",
    default=False,
    is_flag=True,
    help="output raw hexadecimal without encoding"
)
def decrypt_text(password, ciphertext, key, hex):
    """Decrypts the input text with the given key using AES-128. """
    try:
        cipherinput = bytearray.fromhex(ciphertext)
    except ValueError as ve:
        raise click.BadParameter("Input needs to complete bytes in valid hexadecimal")

    iterations = 0 if key else 200000
    keys = prep_password(password, iterations)

    cipherinput = decrypt(cipherinput, keys)
    cipheroutput = remove_padding(cipherinput)

    if hex:
        click.echo(cipheroutput.hex())
    else:
        try:
            click.echo(cipheroutput.decode("utf-8"))
        except UnicodeDecodeError as e:
            raise click.BadParameter(
                "Decryption output was not decodable with utf-8. " \
                "Try with decrypting with the --hex option."
            )


@cli.command("fe")
@click.argument("password")
@click.argument("filepath_in")
@click.option(
    "-k",
    "--key",
    default=False,
    is_flag=True,
    help="use 16-byte hexadecimal key instead of password of arbitrary length"
)
@click.argument("chunksize", callback=validate_chunksize, default = 2**25)
def encrypt_file(password, filepath_in, key, chunksize):
    """Encrypts a file with AES.

    The function processes the file from filepath_in in chunks to avoid
    high memory usage (see variable chunksize).
    """
    iterations = 0 if key else 200000
    keys = prep_password(password, iterations)
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
@click.argument("password")
@click.argument("filepath_in")
@click.option(
    "-k",
    "--key",
    default=False,
    is_flag=True,
    help="use 16-byte hexadecimal key instead of password of arbitrary length"
)
@click.option(
    "-f",
    "--force",
    default=False,
    is_flag=True,
    help="force decryption of files without a .enc file extension. " \
    "Will add a .decrypted extension on the output."
)
@click.argument("chunksize", callback=validate_chunksize, default = 2**25)
def decrypt_file(password, filepath_in, key, force, chunksize):
    """Decrpyts a file with AES.

    The function processes the file from filepath_in in chunks to avoid
    high memory usage (see variable chunksize).
    """
    iterations = 0 if key else 200000
    keys = prep_password(password, iterations)
    b = bytearray(chunksize)
    if not filepath_in.endswith(".enc") and not force:
        raise click.FileError(filepath_in,
            "File has no '.enc'-ending and may not be an encrypted file. " \
            "Run with the -f option if you want to decrypt this file."
        )
    elif force:
        filepath_out = filepath_in + ".decrypted"
    else:
        filepath_out = filepath_in[:-4] # remove .enc file extension
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



def main():
    setup()
    cli()
