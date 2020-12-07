# sbox in decimal
sbox = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]

# round constants in hex
rcons = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]


def expand_key(key):
    """Execute the key schedule for AES.

    Args:
        key: 128-bit hexadecimal key in a list four 32-bit numbers (see format_key function)

    Returns:
        List of 32-bit numbers representing roundkeys resulting from the original input key
    """
    key = format_key_32bit(key)
    w = [word for word in key]

    for i in range(4, 44):
        round = i // 4 - 1
        if i % 4 == 0:  # the first 32-bits of every key get processed differently
            w.append(w[i-4] ^ g(w[i-1], round))
        else:
            w.append(w[i-4] ^ w[i-1])

    # create list of bytes from list of 32-bit numbers
    bytelist = [byte for word in w for byte in separate_into_chunks(word, chunksize=8)]

    return bytearray(bytelist)



def g(word, round):
    """g function for the AES key schedule.

    Args:
        word: 32-bit number
        round: counter for the current round

    Returns:
        32-bit number
    """

    wordlist = separate_into_chunks(word, chunksize=8)

    # Rotate input word
    subword = wordlist[1:] + wordlist[0:1]

    # S-Box substitution
    for idx, v in enumerate(subword):
        subword[idx] = sbox[v]

    # add round constant
    subword[0] = subword[0] ^ rcons[round]

    # combine into one 32-bit number
    return_word = 0
    for idx, s in enumerate(subword):
        return_word += s << (8*(3-idx))

    return return_word


def separate_into_chunks(num, chunksize=8):
    """Recursive splitting of a number into a list of 8-bit numbers.

    Args:
        key: any number

    Returns:
        list of four 8-bit numbers
    """
    compare_constant = 0x01 << chunksize
    return [num] if num < compare_constant else separate_into_chunks(num >> chunksize, chunksize) + [num % compare_constant]


def format_key_32bit(key):
    """Formats hex key string into four 32-bit chunks.

    Args:
        key: string of a 128-bit hex number

    Returns:
        list of four 32-bit numbers
    """
    return separate_into_chunks(int(key, 16), 32)



if __name__ == "__main__":
    key = "2b7e151628aed2a6abf7158809cf4f3c"
    a = expand_key(key)
    assert list(map(hex, a[16:20])) == ["0xa0", "0xfa", "0xfe", "0x17"]
