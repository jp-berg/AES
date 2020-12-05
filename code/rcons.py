def rcon_compute_comprehension():
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


def rcon_compute():
    """rcon_compute_comprehension written differently"""
    rcons = []
    for i in range(10):
        rcon = 0x01 << i
        if rcon < 0xff:
            rcons.append(rcon)
        else:
            rcons.append(rcon ^ (0x11b << i - 8))
    return rcons


if __name__ == "__main__":
    a = rcon_compute()
    b = rcon_compute_comprehension()
    rcons_precomputed = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]
    assert a == rcons_precomputed
    assert b == rcons_precomputed
