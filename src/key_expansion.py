def expand_key(key, sbox):
    """Execute the key schedule for AES.

    Args:
        key: 128-bit hexadecimal key in a list four 32-bit numbers (see format_key function)

    Returns:
        Bytearray of all roundkeys appended.
    """
    key = bytearray.fromhex(key)
    w = [bytes(key[i:i+4]) for i in range(0, 16, 4)]

    rcons = rcon_compute()

    for i in range(4, 44):
        round = i // 4 - 1
        if i % 4 == 0:  # the first 32-bits of every key get processed differently
            w.append(byte_xor(w[i-4], g(w[i-1], round, rcons, sbox)))
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


def g(word, round, rcons, sbox):
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
