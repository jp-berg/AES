from time import perf_counter


def mult_gal(a, b):
    """
    Multiplicates two numbers in the Galois Field specified by the AES-Standard.

    Algorithm specified under
    https://en.wikipedia.org/wiki/Finite_field_arithmetic#multiplication
    as a modiefied version of the "peasant's algorithm"
    Tested with https://www.ece.unb.ca/cgi-bin/tervo/calc2.pl
    """
    p = 0
    for i in range(8):
        if (a == 0) or (b == 0):
            break
        if b & 1:
            p ^= a
        b >>= 1
        a = ((a << 1)%256) ^ (-(a >> 7) & 0x1b)
    return p


def gen_mult_lookup():
    """
    Generates a lookup table for the Galois-field-multiplication
    necessary in AES.
    """
    mult1 = bytearray(256)
    mult2 = bytearray(256)
    mult3 = bytearray(256)

    for i in range(256):
        mult1[i] = i
        mult2[i] = mult_gal(i, 2)
        mult3[i] = mult_gal(i, 3)

    return mult1 + mult2 + mult3


def mult_inv_gal():
    """
    Generates a table of the multiplicative inverse of the Elements
    contained within the AES-Galois-Field.

    It uses an unelegant brute-force-method.
    """
    list_start = [*range(1, 256)]
    list_res = [0]
    for i in range(256):
        for j in list_start:
            if mult_gal(i, j) == 1:
                list_res.append(j)
                list_start.remove(j)
    return bytearray(list_res)


# #https://en.wikipedia.org/wiki/Itoh%E2%80%93Tsujii_inversion_algorithm
# def inv_gal_IT(a):
#     r = ((2**8)-1)
#     ArMin1 = 1
#     for i in range(r-1):
#         ArMin1 = mult_gal(prod, a)
#     Ar = mult_gal(ArMin1, a)


def shift_left(byte, rot):
    """Implements a left bitwise circular shift for bytes."""
    temp = (byte << rot)%256
    byte = temp | ((byte >> (8-rot)))
    return byte


def gen_sbox():
    """Genereates the AES S-box"""
    mult_inv_table = mult_inv_gal()
    sbox = bytearray(256)
    j = 0
    for i in mult_inv_table:
        #affine transformation
        sbox[j] = i ^ shift_left(i, 1) ^ shift_left(i, 2) ^ shift_left(i, 3) ^ shift_left(i, 4) ^ 0x63
        j += 1
    return sbox


def gen_inverse_sbox():
    """Generates the inverse AES S-Box"""
    mult_inv_table = mult_inv_gal()
    inv_sbox = bytearray(256)
    for i in range(256):
        tmp = shift_left(i, 1) ^ shift_left(i, 3) ^ shift_left(i, 6) ^ 0x05
        inv_sbox[i] = mult_inv_table[tmp]
    return inv_sbox
