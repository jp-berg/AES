# Overview

In general we decided on the C programming language for implementing the AES algorithm. The source code for our algorithm is compiled to a "Shared Object", which is then loaded as a "dynamically loaded library" into a Python wrapper, also reffered to as wrapper, which facilitates the interaction with the algorithm. 

The use of two programming languages allows us leverage the advantages of both, while alleviating some shortcomings of both.
The python wrapper provides a command line interface, which enables encryption and decryption of files and text input. The c source code describing the implementation of the AES-algorithm, also reffered to as C-core, has test coverage for every function to ensure correctness.

(graphic?) On calling the wrapper via command line, the program checks, wether there are already .so-files available to link. If the wrapper cannot find them it compiles them from the .c-files. After that it links the libraries and executes the command. It transforms the passed user input, either file or text, into a padded byte-array, and generates the key. There is either a 16-byte hex key made available by the user or it has to be generated via a hash function from a string input by the user. After the key expansion (in Python) both the key and the byte-array with the user input get passed on to the C-core. The core gets a pointer to the array and key. It uses those pointers to transform the user-input-array in place. After the transformation is finished the wrapper just needs to output the transformed byte-array.

Since the only differences between AES and Rijndael are the sizes of the accepted keys and blocks (rijndael, 31) the names for both algorithms will be used synonymously throughout this document.

# Language Choices

We chose to implement the algorithm itself in C, while Python handles the input and output of our program. This allows us to use both languages to their full potential, while avoiding problems of both.

## Python

Python is a popular (instack, octgit) multiparadigm (learningpython 6) programming language. According to (wikipython) it is interpreted, high-level and general purpose. Combining its high usage with its thirty years of age it can be concidered a mature language and as such boasts a fair share of success stories (pythonsuccess)(learningpython 9-10). With over 280000 Packages available via the Python package manager pip it offers a healthy and extensive ecosystem (pythoncommunity). 

With our design we are able to make use of Pythons advantages:
* *Readability*: One of Pythons qualities is its "focus on readability, coherence, and software quality in general" (learningpython 3). C on the other hand is generally concidered to be more difficult to understand, especially because of features and concepts not found in other languages (cmodern 5). This implementation therefore tries to cover as much of the functionality with the easier to read Python.
* *Memory safety*: All memory used by our program is allocated by python. Since it is a garbage-collected language, the program does not have to worry about freeing unused memory. This avoids memory leaks in the program. (learningpython 18)
* *Performance*: Python is on the slow end of programming languages, but that is nearly irrelevant for the purpose it is used in the application. The main task is handling input/output and on modern computers it should be fast enough to read/write from/to the command line or disk, without becoming a bottleneck.
* *Robusteness*: The programming language itself is concidered robust and stable (learningpython 9) input in Python is relativly simple and straightforward. There is no undefined behaviour, input length or encoding issues the programmer has to worry about (compare to https://web.archive.org/web/20201112034702/http://sekrit.de/webdocs/c/beginners-guide-away-from-scanf.html). 
* *Extensebility*: Pythons package manager, import system and large standard library makes it easy to add new features to our program. Adding password hashing for example could be accomplished by simply importing a new package from the standard library and adding a few lines of code. This opens up a lot of possibilites froe extending the functionality of our program in the future. Here Python helps the present implementation to cover up for the lack of a package manager and a less comprehensive standard library (compare https://www.ibm.com/support/knowledgecenter/en/ssw_ibm_i_71/rtref/stalib.htm to https://docs.python.org/3/library/index.html).
* *Productivity*: Python is an dynamically typed (learningpython 9), interpreted language, generating a tight developement loop uninterrupted by compile times, with almost no delay between writing and executing the code. This helps to improve and iterate over the code rapidly, motivating a more exploratory and incremental approach to program developement. Furthermore Python is able to express more functionality in less lines of code than other languages, which helps with readability and mainainability. " It is deliberately optimized for speed of development" (learningpython)(p.5)
* *Portability*: Most Python code is able to run unmodified on "all major computer platforms"(learningpython 4, 17-18). Combined with the portability of C our program is only limited by its ability to execute the compilation of the C-core, which for now is bound by the ability of Python dispatching the compile command to GCC or Clang, which for now was only tested on Ubuntu.

## C

C is, like Python, one of the most popular programming languages today (instack, octgit). It is close to 20 years older than Python though, dating back to the early 1970s (cmodern 2). It is statically typed (modernc, 40), compiled (cmodern, 2), low-level (meaning providing access to concepts more commonly found on the machine level) (cmodern, 4) and provides interfaces for manual memory management, but no build in garbage collection (cpointers, 55). One of the more notable projects written in C is the Linux kernel, the basis for the widely used Linux operating system (https://www.kernel.org/doc/html/latest/process/programming-language.html). 
C is concidered one of the fastest and most efficient languages (https://benchmarksgame-team.pages.debian.net/benchmarksgame/), but is more error-prone than othes (modernc 5). One has to be careful to avoid so called "undefined behaviour", buffer overflows (since c-arrays are not bounds-checked), and memory management bugs. 
A popular example of a serious bug that gets attributed to the fact that C is more error-prone than other languages is Heartbleed. A programming mistake so serious, that "Some might argue that it is the worst vulnerability found (at least in terms of its potential impact) since commercial traffic began to flow on the Internet." (https://www.forbes.com/sites/josephsteinberg/2014/04/10/massive-internet-security-vulnerability-you-are-at-risk-what-you-need-to-do/). (wheeler, https://dwheeler.com/essays/heartbleed.html) sees this as a direct result of C not including "any built-in detection or countermeasure for improper restriction of buffers" (ch. 3.9) and states that one of "the most dangerous widely-used languages for security-relevant software \[is\] C". This type of vulnerability is "widely used" often with "catastrophic effect" , but "Using or switching to almost any other language (other than C, C++, or Objective-C) would completely eliminate buffer-related vulnerabilities, including Heartbleed." (ch. 3.9.1)
The following list illustrates how the program uses the advantages of C, while avoiding the shortcomings of the language:

* *Speed*: Since C is concidered a fast language (cmodern, 4) it is not unusual to rewrite calculation intensive parts of programs in C, even if the project is written in another language (https://www.youtube.com/watch?v=e08kOj2kISU 24:33). Python itself uses this architectural concept, interfacing with compiled C code to make use of Cs speed advantage for certain tasks, like (learningpython 7) explains. The author even recommends to create compiled extensions for "domains that do require op-
timal execution speeds" and linking those back into the Python code. The calculation intensive part of our project is clearly the AES encryption itself, especially with growing file size.
* *no memory management necessary*: Due to the fact that the C-core operates on byte-arrays allocated by Python, nothing needs to be allocated on heap. Since the rest of the data needed is allocated on the stack all memory used is automatically freed after the encryption function returns, without the need for the programmer to intervene. This avoids memory leaks occuring when an allocation on the heap is not met with a call to free() after the allocated memory is not needed anymore. So called double free errors are also avoided, meaning there is no risk of freeing the same area of memory twice. This error could potentially corrupt the programs's memory management data structures and crash the program (cpointers, p.49).
* *straightforward implementation*: The algorithm described in (fips197) translates well to C code. No special imports are needed, no hard-to-understand operations are required to be executed and the described pseudocode functions map very cleanly to C functions. The AES-algorithm itself makes extensive use of Galois-Field-operations in \[2^8\]. Those can be easily expressed through the native uint8_t C-data-type, which represents an unsigned byte. Buffer overruns are avoided, because the array AES operates on is allocated by Python. Since Python tracks the length of any object allocated and since we pass the length of the array as a boundary, buffer overruns are highly unlikely. This is one example of how the C-core can stay simple, because the wrapper ensures the data has the right format.
* *fast compile times*: Since the C-core encompasses only a few hundred lines of code it compiles in subsecond time on our development machines, even with optimization enabled. This encourages trying new things and helps to get quick feedback even for small changes, either through the static analyzer of the compiler itself or through the included testing libraries.
* *portability* C compiles to numerous plattforms  and operating systems. (https://gcc.gnu.org/install/specific.html) demonstrates how many architectures and operating systems can be reached with one compiler. Since the C-core tries to avoid any platform specifics or targeting specific compilers, it should not be the limiting factor in terms of portability, especially since the reference implementation of Python is written partially in C (https://github.com/python/cpython), which means Python is not able to target CPU architectures or operating systems C cannot run on.

# AES - preliminaries

The Advanced Encryption Standard has a series of defining properties.

* *symmetric cipher*: The key that encrypts a message is the same key that decrypts it. This is in contrast to asymetric cryptography, where encryption and decryption key differ from each other.
* *block cipher*: AES only operates on blocks with an exact size of 128 bits at a time. If there are bitsequences whose length is not cleanly divisible by 128, they have to be padded in order to be encrypted. With that the algorithm differs for example from the so called stream-ciphers, which encrypt a digit stream one plaintext digit at a time with one corresponding digit from a second stream, called key stream, which in turn is generated pseudorandomly from a key. The combination of plaintext digits with keysteam digits creates the cipherstream.
* *key-iterated*: The Advanced Encryption Standard belongs to the class of key-iterated block ciphers, because encryption (and thus decryption) is achieved by applying a round transformation on the plaintext multiple times. (rijndael)
* *byte-oriented*: The smallest unit the algorithm operates on is a byte, which represents eight bits at a time (fips197)
* *key-length*: AES supports three different key lengths: 128 bits, 192 bits and 256 bits. The different key length are accompanied by differing numbers of rounds. AES-128 uses ten rounds, AES-192 twelve and AES-256 utilises fourteen rounds. (fips197)
* *state*: The two-dimensional 4x4 array of bytes on which AES performs its operations on is called state. 

# The wrapper

This chapter describes the Python-wrapper 'wrapper.py' in more detail. Since it is not the focus of the documentation this chapter is kept shorter than the documentation about the C-core implementing AES.

In general the wrapper is supposed to prepare data and to provide an interface for the C-core. It is the entry point to the program. The basic functionality from a user perspective can be broken down into 3 components.

## Compiling the C-core

To guarantee optimal performance and portability the present implementation compiles the C-source code into linkable binaries on first startup. The program does get delivered with an empty lib-folder. On startup, the program tries to link the libraries containing the AES C-code compiled to binaries from the lib-folder. If it cannot detect them, it tries to compile them via Clang or GCC. A successful compilation guarantees that the C-core is able to run on the platform it was compiled to. Furthermore the compiler may be able to leverage platform specific optimizations if they are available. Since compilation time is short and done only once it is a reasonable way to ensure portability and performance.
Finally it made testing changes to the C-code easier, since one only had to delete the old library files and run the code again to trigger a recompile.

## en- and decryption

The C-code, once it is compiled to a .so-file, can be dynamically linked with the Python standard-library ctypes. This allows calling C functions directly from Python and passing pointers to Python bytearrays. Those bytearrays can be modified directly by the called C-code. The wrapper calls the en- and decrypt functions of the C implementations via the two python functions "encrypt" and "decrypt", that both take the byte array that is supposed to be processed and the expanded keys. The two functions then prepare the arrays for the ctypes interface and pass them on to the C-function for en- and decryption, along with the initvals, which consists of the values for the S-box and the values of the GFMLT (both generated at program startup) concatenated with the expanded keys. Since the C-core modifies the byte arrays in place they just get returned, after the C-function returns.

## Interface

There are four functions through which the user interacts with the program: two for text operations and two for file operations. All four get exposed to the user via the 'click'-library, which a following chapter will explain in more depth. This library passes on the arguments from the command line to the function it decorates. ITERATION

The text functions, called 'te' for '**t**ext **e**ncrypt" and 'td' for '**t**ext **d**ecrypt' via the command line, simply encode the recieved text into a bytearray (and add padding or remove it), expand the key, call the matching en- or decryption function with both of those arrays and return either the encrypted text in hex or the decrypted text in utf-8 encoding. 

The file functions, called 'fe' for '**f**ile **e**ncrypt" and 'fd' for '**f**ext **d**ecrypt' via the command line, work in a similar way. They also expand the key, but additionally prepare an outputfile, by either adding or removing the ".enc"-fileending. They open both the input and output file simultaneously. This helps with very large files, since they can process them chunk by chunk. This allows for (theoretically) processing files of unbounded filesizes, since the program is not limited by the systems RAM. For every chunk the program reads, it checks if the read length is shorter than the defined length of a chunk. If thats the case the program knows that this is the last chunk of the file. It either pads the last chunk (in case of encryption) or removes the padding (in case of decryption), terminates the read-loop and writes them to disk with the other chunks. During the process the chunks themselves get passed on to the respective en- or decryption function, along with the expanded keys.



# Possible areas of future improvements

This chapter is a collection of ideas, which could bring potential improvements to the project in the future.

## AES-192 and AES-256

Currently the implementation only supports AES with key sizes of 128 bits, but it would be possible to also support other lengths of the standard, namely key lengths of 192 and 256 bits. Changes to the AES code itself would be minimal since the only difference would be the number of rounds, which is already a flexible parameter in the encryption implementation. The prep_password-function has to be tweaked, but the used hashing function makes adjusting the key length easy. 
The test would have to be modified too, although this modification seems more like a hassle than a challenge since the logic that is already in place for AES-128 only needs to be adjusted for the additional key sizes.

## Parallelism

Since AES encrypts blocks independently from each other the algorithm can be categorized as an so called embarrasingly parallel problem (parallelprog)(ch.2.4.2). Consequently an easy avenue for gaining more speed seems to be restructuring the program in such a way, that every available CPU-core gets put to work on a seperate series of blocks to encrypt/decrypt. On short encryption operations in the kilobyte range this may not deliver a conciderable performance increase, but since the present implementation is able to operate on files of unbounded file size the time saving possibilites become apparent quite fast.

A simple way to archive such parallelism could for example lead through the OpenMP-library. This library was designed to provide a shared-memory API that allows the program to execute in parallel and is added into the program fairly easily (paralelprog ch.5). Since the encryption of multiple blocks can be expressed as a for-loop, OpenMPs 'parallel for'-directive may be an easy way to execute the program on multiple cores (compare (parallelprog) ch 5.5).

## T-tables

The present implementation already makes use of lookup tables. (rijndael 59) proposes a method that makes even more extensive use of lookup tables, which needs only 4 array accesses and 4 bitwise XOR operations for each round and 4-byte column. They budget in 4kb of memory for the lookup tables. This is a negligible amount of memory compared to the gigabytes available on modern x86-systems.

## No constant value calculations

To fullfill the task of this seminar it was explicitly required to (re-) calculate values, that could as well be hardcoded. The additional space used by this is calculated as follows: 
The GFMLT for multiplication with two and three can be stored in 2 * 256 bytes (multiplication with one does not need to be stored, since it just results in the unmodified value itself). The Sbox and Inverse Sbox are 256 additional bytes each, which brings us to a total of 1024 additonal bytes of memory. This is concidered to be a negligible size increase, but saves on recalculating the values on program startup.

## Block cipher mode of operation

Due to time constraints, it was not possible to implement a different block cipher mode of operation, but it is something the current implementation would greatly benefit from. Chapter XXX goes more in-depth regarding this topic.

## File-header: ARGON2-Hashing algorithm and HMAC

At the moment the passwords are hashed with PBKDF2. This algorithm can unfortunately easily be cracked with the right hardware, like (appcrypt 697, 701) explains and suggests using the password hashing competition winner argon2, which is designed to withstand bruteforcing attemts by being able to use more memory and parallelism, thus making it more expensive for an attacker to guess the password.
The argon2-parameters would either have to be hardcoded or attached to the encrypted text in a header for example.
If such a header would be added, it seems like a logical step to also add a public salt to the hash parameters specified within. A salt is a random string, regenerated for each new password, that is hashed along with the password to prevent any kind of preprocessing attack on the password hash. The salt itself is stored in the clear. (appcrypt 693) At the moment the hash is hardcoded to "aeskurs", but in the future would consist of a randomly generatet string from "os.urandom()".
The header could also hold the hash for the hash based message authentication code or short HMAC (paar)(ch.12.2.3). This would ensure integrity of the message, i.e. that the encrypted data was not changed, for example during transit by a malicious third party. This is archieved by hashing the message before transmission in combination with a secret shared only by the communicating parties and appending the resulting hash to the message. The recieving party is then able to verify the integrity of the message by repeating the steps and comparing the generated and the appended hash.
(moxie) recommends to authenticate first before performing any cryptographic operation, so a future implementation would probably first encrypt the message, then hash it and append the hash to the header. Since we want to ensure that the correct password-hashing parameters were recieved, those would be also fed into the HMAC if a future implementation makes use of said parameters. The HMAC algorithm would probably a SHA3-variant, as specified in (fips202), providing the HMAC with adequate cryptographic strength.






---
* GFMLT Galois Field multiplication lookup table
* I/O: input/output
