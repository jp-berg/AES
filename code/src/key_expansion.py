# sbox in decimal
sbox = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]


def expand_key(key):
    """Execute the key schedule for AES.

    Args:
        key: 128-bit hexadecimal key in a list four 32-bit numbers (see format_key function)

    Returns:
        Bytearray of all roundkeys appended.
    """
    key = bytearray.fromhex(key)
    keywords = [bytes(key[i:i+4]) for i in range(0, 16, 4)]

    w = [word for word in keywords]

    rcons = rcon_compute()

    for i in range(4, 44):
        round = i // 4 - 1
        if i % 4 == 0:  # the first 32-bits of every key get processed differently
            w.append(byte_xor(w[i-4], g(w[i-1], round, rcons)))
        else:
            w.append(byte_xor(w[i-4], w[i-1]))

    return bytearray(b''.join(word for word in w))


def byte_xor(ba1, ba2):
    """Execute XOR on two bytestrings.

    Args:
        None

    Returns:
        The bitwise XOR of two bytestrings.
    """
    return bytes([a ^ b for a, b in zip(ba1, ba2)])


def g(word, round, rcons):
    """g function for the AES key schedule.

    Args:
        word: 32-bit number
        round: counter for the current round

    Returns:
        32-bit number
    """

    # Rotate input word
    subword = bytearray(word[1:] + word[0:1])

    # S-Box substitution
    for idx, v in enumerate(subword):
        subword[idx] = sbox[v]

    # add round constant
    subword[0] = subword[0] ^ rcons[round]

    return bytes(subword)


def rcon_compute():
    """Computes the round constants for the AES key expansion.

    The formula for the round constant in round i is 2^i-1 in GF(128).
    The irreducable polynomial to get back into the finite field after
    multiplications is represented as 0b100011011 or 0x11b or 283.

    For numbers larger than 255 (0xff) the result of a bitshift by one (representing
    times two in binary) would overflow into 9-bits. In these cases the resulting
    number XOR the magic polynomial shifted by as many bits as the number is over 8
    will result in a number in the finite field.

    The function return the following values
    [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]

    Args:
        None

    Returns:
        List of ints representing the round constants
    """
    return [
        0x01 << i
        if 0x01 << i < 0xff
        else 0x01 << i ^ (0x11b << i - 8)
        for i in range(10)
    ]
