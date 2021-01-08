## LIMITATIONS OF THIS VERSION
* Pytest testing currently does not work in this file structure, thus the testing files have been excluded from this release.
* There is no setuptools integration yet, missing packages need to be installed manually.
  * those packages include click, ctypes, maybe some others as well
* only encryption of utf-8 encoded text from the commandline is supported


## Files
The `/src` directory contains the C-files with the encryption and decryption algorithms. The `/lib` directory is created on first run and will contain the compiled C-libraries.

## Usage
Simply run `python3 wrapper.py --help` for instructions.

For example encryption looks like `python3 wrapper.py encrypt CIPHERTEXT KEY`.
