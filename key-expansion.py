# sbox in decimal
sbox = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]
rcons = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]

def key_expand(key):
    # create output keyvector
    w = []
    for word in key:
        w.append(word)

    for i in range(4, 44):
        round = i // 4 - 1
        if i % 4 == 0:
            # compute g function
            w.append(w[i-4] ^ g(w[i-1], round))
        else:
            w.append(w[i-4] ^ w[i-1])

    return w



import time

def seconds_func(key):
    a = time.time()
    extact_recursvie(key)
    b = time.time()
    c = time.time()
    extact_the_c_way(key)
    d = time.time()
    return [(b-a)*10**6, (d-c)*10**6]

def extact_recursvie(key):
    return [key] if key < 0x100 else extact_recursvie(key >> 8) + [key % 0x100]

def extact_the_c_way(word):
    wordlist = []
    tmp = word
    for i in range(4):
        wordlist.append(tmp % 0x100)
        tmp = word >> 8
    return(list(map(hex, wordlist)))


def g(word, round):
    wordlist = []
    tmp = word
    for i in range(4):
        wordlist.append(tmp % 0x100)
        tmp = tmp >> 8
    wordlist = wordlist[::-1]

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



def format_key(key):
    """Formats hex key string into 4 chonks"""
    key_formatted = [int(key[a:a+8], 16) for a in range(0, len(key), 8)]
    return key_formatted




if __name__ == "__main__":
    key = "2b7e151628aed2a6abf7158809cf4f3c"
    # test_key = [0x09, 0xcf, 0x4f, 0x3c]
    # print([hex(i) for i in g(test_key, 1)])
    a = key_expand(format_key(key))
    hexlist = list(map(hex, a))
    print(hexlist)
    assert a[4] == 0xa0fafe17




def timing_test():
    resulties = []
    for i in range(1000):
        resulties.append(seconds_func(0x8090a0b))
    recursvie = [a[0] for a in resulties]
    cliek = [a[1] for a in resulties]
    avg_rec = sum(recursvie)/len(recursvie)
    avg_c = sum(cliek)/len(cliek)
    print(avg_rec, avg_c)
