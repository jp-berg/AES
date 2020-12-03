import time


def seconds_func(key):
    a = time.time()
    separate_into_8bit_chunks_recursive(key)
    b = time.time()
    c = time.time()
    separate_into_8bit_chunks_iterative(key)
    d = time.time()
    return [(b-a)*10**6, (d-c)*10**6]


def separate_into_8bit_chunks_recursive(key):
    return [key] if key < 0x100 else separate_into_8bit_chunks_recursive(key >> 8) + [key % 0x100]


def separate_into_8bit_chunks_iterative(word):
    wordlist = []
    tmp = word
    for i in range(4):
        wordlist.append(tmp % 0x100)
        tmp = tmp >> 8
    return wordlist


def timing_test():
    resulties = []
    for i in range(1000):
        resulties.append(seconds_func(0x8090a0b))
    recursvie = [a[0] for a in resulties]
    cliek = [a[1] for a in resulties]
    avg_rec = sum(recursvie)/len(recursvie)
    avg_c = sum(cliek)/len(cliek)
    print(avg_rec, avg_c)

if __name__ == '__main__':
    timing_test()
