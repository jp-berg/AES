# rcons precomputed for comparison
rcons = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]


magic_polynomial = 0b100011011 # magic AES polynomial


def rcon_compute():
    """Computes the round constants needed for the AES key schedle
    """
    rcons = []
    for i in range(10):
        rcon = 0x02 ** i
        print(rcon)
        if rcon > 0xff:
            rcons.append(rcon ^ magic_polynomial)
        else:
            rcons.append(rcon)
    return rcons


def rcon_compute_oneliner():
    return [0x02**i ^ magic_polynomial if 0x02**i > 0xff else 0x02**i for i in range(10)]


if __name__ == "__main__":
    computed = rcon_compute()
    print(list(map(hex, computed)))
    assert computed == rcons
