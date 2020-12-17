import ctypes
from os.path import isfile, join, splitext, expanduser
from os import cpu_count, getcwd, urandom
from subprocess import check_output
from getpass import getpass
import hashlib

from key_expansion import expand_key, format_key_32bit

compile_gcc = """gcc -O2 -w -shared -fpic -Wl,-soname,AES
                -o libaes.so AES.c -fopenmp""".split()
compile_clang = """clang -O2 -w -shared -fpic -Wl,-soname,AES
                -o libaes.so AES.c -fopenmp""".split()
cpucount = cpu_count()
chunksize = 2**30 #needs to be a multiple of 16 (otherwise padding is needed)

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
aeslib = ctypes.CDLL(join(getcwd(),"libaes.so"))             


def prep_password(pwd):
    """
    Generates bytearray containing the consecutive
    round keys from an arbitrary string.
    """
    #Use higher iteration values (>3000000) for more security:
    p = hashlib.pbkdf2_hmac(hash_name = 'sha256',
                            password = pwd.encode("utf-8"),
                            salt = "1234".encode("utf-8"),
                            iterations = 10, dklen = 16) 
    return expand_key(p.hex())


def pad_bytearray(len_ba):
    """Generates Bytearray with random values for padding AES-input.

    Args:
        len_ba: length of the bytearray that (may) needs padding

    Returns:
        Bytearray b, that completes an Bytearray with the length len_ba
        in a way that (len_ba + len(b)) % 16 == 0 . Last byte indicates
        length of b, i.e. the number of bytes to be discarded from the
        end of the decrypted file.
    """
    topad = 16 - len_ba % 16
    # Add padding, even if not needed (to guarantee consistency
    # in purpose of the last byte of a file):
    if not topad:
        topad = 16 
    b = bytearray(urandom(topad))
    b[topad - 1] = topad
    return bytearray(b)


def encrypt_aes(toencrypt, key):
    """Encrypts a bytearray with AES using a key.

    Args:
        toencrypt: Bytearray that is supposed to be encrypted.
            Length must be a multiple of 16.
        key: Bytearray with roundkeys for encryption.
            Must have a length of 11 (rounds) * 16 (bytes) = 176

    Returns:
        Bytearray with encrypted Bytes
    """
    toencrypt = bytearray(toencrypt)
    if len(toencrypt)%16 != 0:
        raise ValueError("Bytearray needs padding for encryption, but has none")
    byte_array_key = ctypes.c_ubyte * len(key)
    byte_array_file = ctypes.c_ubyte * len(toencrypt)
    aeslib.encryptBlocks(byte_array_file.from_buffer(toencrypt),
                         byte_array_key.from_buffer(key), len(toencrypt), 10)
    return toencrypt


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
    b = bytearray(chunksize)
    cont = True
    filepath_out = splitext(filepath_in)[0] + ".enc" # add new fileending
    with open(filepath_in, "rb") as file_in:
        with open(filepath_out, "wb") as file_out:
            while cont:
                b = file_in.read(chunksize)
                if len(b) < chunksize:
                    b += pad_bytearray(len(b)) #pad last chunk
                    cont = False
                b = encrypt_aes(b, key)
                file_out.write(b) 


   
if __name__ == "__main__":
    filepath_in = ""
    while not filepath_in:
        filepath_in = expanduser(input("Provide a filepath: "))
        if not isfile(filepath_in):
            print("Not a valid filepath!")
            filepath_in = ""
    key = ""
    key2 = ""
    while not key:
        key = getpass()
        key2 = getpass("Repeat:")
        if key != key2:
            print("Passwords do not match")
            key = ""

    key = prep_password(key)
    encrypt_file(filepath_in, key)
        
    
    
    

    



            
    
    
        
    

