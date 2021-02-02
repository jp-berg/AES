# AES
This program implements several modes of the AES-128 algorithm to encrypt and decrypt data.

## Files
The `src/` directory contains the C-files with the encryption and decryption algorithms. The `lib/` directory is created on first run and will contain the compiled C-libraries. Tests to be run with pytest are found in the `tests/` directory.

## Installation
The program is written in C and Python3. It requires a current python interpreter as well as a compiler for the parts written in C. The requirements are:
* Python 3.6 or newer (with the pip/pip3 installed)
* a current version of gcc/clang (has to be on PATH as well)
* a Unix-Like operating system (or subsystem like the WSL on Windows)

If the above requirements are met, copy the program to the desired location. Optionally you could use `pyenv` or `virtualenv` to create a virtual python environment to run in.
In order to install the python dependencies run: `pip3 install -r requirements.txt`.
On the first execution of the program, the .c files contained within the `src/` directory will be compiled into system specific shared object libraries. On later executions the libraries will be reused and not recompiled.  

Optionally you can add the program directory to your `PATH` and simply run it from anywhere with `aes`. You probably should not do that though, as this program is immature and not meant for production.

## Usage
For a quick start simply run `./aes --help`.

The program has four main commands and corresponding modes of operation:
* text encrypt `te`
* text decrypt `td`
* file encrypt `fe`
* file decrypt `fd`

To get help on each command run `./aes [COMMAND] --help`

### Text Encrypt
The command `te` makes the program encrypt a text given on the command line. The command is structured as follows:
```
aes te [OPTIONS] PASSWORD CIPHERTEXT

Options:
-k, --key  use 16-byte hexadecimal key instead of password of arbitrary length
-h, --hex  interpret the input as pure unencoded hexadecimal bytes
```

The `PASSWORD` argument takes a string of arbitrary length and creates a key out of it. If you want to give an explicit AES-128 16 byte key, use the `-k/--key` option. The `CIPHERTEXT` argument takes the text to be encrypted. By default it is interpreted as `UTF-8`. If you want to explicitly give raw hexadecimal input, use the `-h/--hex` option.

Usage of the command with password `correcthorsebatterystaple` and text "https://xkcd.com/936/" would look like this:
```
> ./aes te correcthorsebatterystaple "https://xkcd.com/936/"
495bdfc4470ba9b320d1dffcc6b58f762fa21f4624d846803d08f3e236dac08b
```

Encryption of the same text with an explicit hexadecimal key would look like this:
```
> ./aes te --key 0000ffff0000ffff0000ffff0000ffff "https://xkcd.com/936/"
690beeaa673a942e5035d2f771a7c5683e8bd069afc4b3d5f5201d4f90f30a37
```

Encryption of a sample block from the FIPS 197 AES standard document would look like this:
```
> ./aes te --key 000102030405060708090a0b0c0d0e0f --hex 00112233445566778899aabbccddeeff
69c4e0d86a7b0430d8cdb78070b4c55a
```

### Text Decrypt
The command `td` makes the program decrypt a ciphertext given on the command line. The command is structured as follows:
```
aes td [OPTIONS] PASSWORD CIPHERTEXT

Options:
  -k, --key  use 16-byte hexadecimal key instead of password of arbitrary length
  -h, --hex  output raw hexadecimal without encoding
```
The `PASSWORD` argument takes a string of arbitrary length and creates a key out of it. If you want to give an explicit AES-128 16 byte key, use the`-k/--key` option. `CIPHERTEXT` argument takes the text to be decrypted. By default the output will be decoded `UTF-8`. If you want to see the raw hex output instead, or if you expect the output to not be `UTF-8` decodable, use the`-h/--hex` option.

Usage of the command with password `correcthorsebatterystaple` and an encrypted text would look like this:
```
> ./aes td correcthorsebatterystaple
>      495bdfc4470ba9b320d1dffcc6b58f762fa21f4624d846803d08f3e236dac08b
https://xkcd.com/936/
```

Decryption of the sample block from FIPS 197 has the following input and output:
```
> ./aes td --key 000102030405060708090a0b0c0d0e0f --hex 69c4e0d86a7b0430d8cdb78070b4c55a
00112233445566778899aabbccddeeff
```

### File Encrypt
The command `fe` makes the program encrypt a given file with AES-128. The command is structured as follows:
```
aes fe [OPTIONS] PASSWORD FILEPATH_IN [CHUNKSIZE]

Options:
  -k, --key  use 16-byte hexadecimal key instead of password of arbitrary length
```
The `PASSWORD` argument takes a string of arbitrary length and creates a key out of it. If you want to give an explicit AES-128 16 byte key, use the `-k/--key` option. The `FILEPATH_IN` argument takes a relative or absolute path to the file to be encrypted. The output file will have the same name and location as the input file, only with the `.enc` file extension added. The program processes the file in chunks of size 33554432 bytes (33 MB). Optionally the chunksize can be changed by giving it at the end of the command.

Encryption of the local file `foo` with password `correcthorsebatterystaple` would look like this:
```
> ./aes fe correcthorsebatterystaple foo
```
The output is the file `foo.enc`.

### File Decrypt
The command `fd` makes the program decrypt a given file with AES-128. The command is structured as follows:
```
aes fd [OPTIONS] PASSWORD FILEPATH_IN [CHUNKSIZE]

Options:
-k, --key    use 16-byte hexadecimal key instead of password of arbitrary length
-f, --force  force decryption of files without a .enc file extension.
             Will add a .decrypted extension on the output.
```
The `PASSWORD` argument takes a string of arbitrary length and creates a key out of it. If you want to give an explicit AES-128 16 byte key, use the `-k/--key` option. The `FILEPATH_IN` argument takes a relative or absolute path to the file to be decrypted. The command expects a file with the `.enc` file extension. If you want to decrypt a file without that extension use the `-f/--force` option.

Decrypting the local file `foo.enc` with password `correcthorsebatterystaple` requires the following input:
```
> ./aes fd correcthorsebatterystaple foo.enc
```
The output is the file `foo`.

Decryption of an encrypted local file `bar` with the `.enc` file extension looks like this:
```
> ./aes fd --force correcthorsebatterystaple bar
```
The output will be the file `bar.decrypted`.

## Testing
For testing install pytest via pip and simply run it in the program root.

## Limitations and Warnings
Do not use in production under any circumstances.
File en- and decryption might overwrite existing files without warning.
For multi-block encryption only ECB mode is implemented which is not very secure.
The password salt to create keys for arbitrary length passwords is fixed and hardcoded. This is also not very secure.
