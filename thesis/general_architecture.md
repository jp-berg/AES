# Overview

In general we decided on the C programming language for implementing the AES algorithm. The source code for our algorithm is compiled to a "Shared Object", which is then loaded as a "dynamically loaded library" into a Python wrapper, also reffered to as wrapper, which facilitates the interaction with the algorithm. 

The use of two programming languages allows us leverage the advantages of both, while alleviating some shortcomings of both.
The python wrapper provides a command line interface, which enables encryption and decryption of files and text input. The c source code describing the implementation of the AES-algorithm, also reffered to as C-core, has test coverage for every function to ensure correctness.

(graphic?) On calling the wrapper via command line, the program checks, wether there are already .so-files available to link. If the wrapper cannot find them it compiles them from the .c-files. After that it links the libraries and executes the command. It transforms the passed user input, either file or text, into a padded byte-array, and generates the key. There is either a 16-byte hex key made available by the user or it has to be generated via a hash function from a string input by the user. After the key expansion (in Python) both the key and the byte-array with the user input get passed on to the C-core. The core gets a pointer to the array and key. It uses those pointers to transform the user-input-array in place. After the transformation is finished the wrapper just needs to output the transformed byte-array.

# Language Choices

We chose to implement the algorithm itself in C, while Python handles the input and output of our program. This allows us to use both languages to their full potential, while avoiding problems of both.

## Python

Python is a popular (instack, octgit) programming language. According to (wikipython) it is interpreted, high-level and general purpose. Combining its high usage with its thirty years of age it can be concidered a mature language and as such boasts a fair share of success stories (pythonsuccess). With over 280000 Packages available via the Python package manager pip it offers a healthy and extensive ecosystem (pythoncommunity). 

With our design we are able to make use of Pythons advantages:
* *Memory safety*: All memory used by our program is allocated by python. Since it is a garbage-collected language, we do not have to worry about freeing unused memory. This avoids memory leaks in the program.
* *Speed*: Python is on the slow end of programming languages, but that is nearly irrelevant for the purpose it is used in the application. The main task is handling input/output and on modern computers it should be fast enough to read/write from/to the command line or disk, without becoming a bottleneck
* *Robusteness*: Reading input in Python is relativly simple and straightforward. There is no undefined behaviour, input length or encoding issues the programmer has to worry about. 
* *Extensebility*: Pythons package manager, import system and large standard library makes it easy to add new features to our program. Adding password hashing for example could be accomplished by simply importing a new package from the standard library and adding a few lines of code. This opens up a lot of possibilites froe extending the functionality of our program in the future.

## C

C is, like Python, one of the most popular programming languages today. It is close to 20 years older than Python though. It is statically typed, compiled and has no build in garbage collection. One of the more notable projects written in C is the Linux kernel, the basis for the widely used Linux operating system. 
C is concidered one of the fastest and most efficient languages, but is more error-prone than other languages. One has to be careful to avoid so called "undefined behaviour", buffer overflows (since c-arrays are not bounds-checked), and memory management bugs. The following list illustrates how the program uses the advantages of C, while avoiding the shortcomings of the language:

* *Speed*: Since C is concidered a fast language it is not unusual to rewrite calculation intensive parts of programs in C, even if the project is written in another language. The calculation intensive part of our project is the AES encryption itself, especially with growing file size.
* *no memory management necessary*: Since the C-core operates on byte-arrays allocated by Python, nothing needs to be allocated on heap. Since the rest of the data needed is allocated on the stack all memory used is automatically freed after the encryption function returns, without the need for the programmer to intervene. This avoids memory leaks occuring when an allocation on the heap is not met with a call to free() after the allocated memory is not needed anymore. So called double free errors are also avoided, meaning there is no risk of freeing the same area of memory twice. This error could potentially corrupt the programs's memory management data structures, crash the program or alter the execution flow.
* *straightforward implementation*: The algorithm described in XXX translates well to C code. No special imports are needed, no hard-to-understand operations are required to be executed and the described pseudocode functions map very cleanly to C functions. The AES-algorithm itself makes extensive use of Galois-Field-operations in \[2^8\]. Those can be easily expressed through the native uint8_t C-data-type, which represents an unsigned byte.
* *fast compile times*: Since the C-core encompasses only a few hundred lines of code it compiles in subsecond time on our development machines, even with optimization enabled. This encourages trying new things and helps to get quick feedback even for small changes, either through the static analyzer of the compiler itself or through the included testing libraries.

# AES - preliminaries

The Advanced Encryption Standard has a series of defining properties.

* *symmetric cipher*: The key that encrypts a message is the same key that decrypts it. This is in contrast to asymetric cryptography, where encryption and decryption key differ from each other.
* *block cipher*: AES only operates on blocks with an exact size of 128 bits at a time. If there are bitsequences whose length is not cleanly divisible by 128, they have to be padded in order to be encrypted. With that the algorithm differs for example from the so called stream-ciphers, which encrypt a digit stream one plaintext digit at a time with one corresponding digit from a second stream, called key stream, which in turn is generated pseudorandomly from a key. The combination of plaintext digits with keysteam digits creates the cipherstream.
* *key-iterated*: The Advanced Encryption Standard belongs to the class of key-iterated block ciphers, because encryption (and thus decryption) is achieved by applying a round transformation on the plaintext multiple times. (rijndael)
* *byte-oriented*: The smallest unit the algorithm operates on is a byte, which represents eight bits at a time (fips197)
* *key-length*: AES supports three different key lengths: 128 bits, 192 bits and 256 bits. The different key length are accompanied by differing numbers of rounds. AES-128 uses ten rounds, AES-192 twelve and AES-256 utilises fourteen rounds. (fips197)
* *state*: The two-dimensional array of bytes on which AES performs its operations on is called state. 
# Possible areas of future improvements

Here are some areas, in which this project could be improved in the future.

## AES-192 and AES-256

Currently the implementation only supports AES with key sizes of 128 bits, but it would be possible to also support other lengths of the standard, namely key lengths of 192 and 256 bits. Changes to the AES code itself would be minimal since the only difference would be the number of rounds, which is already a flexible parameter in the encryption implementation. The prep_password-function has to be tweaked, but the used hashing function makes adjusting the key length easy. 
The test would have to be modified too, although this modification seems more like a hassle than a challenge since the logic that is already in place for AES-128 only needs to be adjusted for the additional key sizes.

## T-tables

## No constant value calculations

To fullfill the Task of this seminar it was explicitly required to (re-) calculate values, that could as well be hardcoded. The additional space used by this is calculated as follows: 
The GFMLT for multiplication with two and three can be stored in 2 * 256 bytes (multiplication with one does not need to be stored, since it just results in the unmodified value itself). The Sbox and Inverse Sbox are 256 additional bytes each, which brings us to a total of 1024 additonal bytes of memory. This is concidered to be a negligible size increase, but saves on recalculating the values on program startup.

## Block cipher mode of operation

## File-header: ARGON2-Hashing algorithm and HMAC

At the moment the passwords are hashed with sha-256. Since this algorithm is quite fast to execute, especially when implemented in hardware, it can be easier to bruteforce passwords that are hashed this way. A better way to secure the password would be by using the password hashing competition winner argon2, which is designed to withstand bruteforcing attemts by being able to use more memory and parallelism, thus making it more expensive for an attacker to guess the password. 
The argon2-parameters would either have to be hardcoded or attached to the encrypted text in a header for example.
The header could also hold the hash for the hash based message authentication code or short HMAC. This would ensure that the encrypted data was not changed, for example during transit. (moxie) recommends to authenticate first before performing any cryptographic operation, so the implementation would probably first encrypt the message, then hash it and append the hash to the header. Since we want to ensure that the correct password-hashing parameters were recieved, those would be also fed into the HMAC if a future implementation makes use of said parameters. The HMAC algorithm would probably a SHA3-variant, as specified in (fips202), providing the HMAC with adequate cryptographic strength.





---
* GFMLT Galois Field multiplication lookup table
