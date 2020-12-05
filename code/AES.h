#ifndef AES
#define AES

#include <stddef.h>
#include <inttypes.h>

void genMultLookup(uint8_t multlookup[3][256]);

inline void AddRoundKey(uint8_t *bytes, uint8_t *keys);
inline void SubBytes(uint8_t *bytes);
void ShiftRows(uint8_t *block);
void MixColumns(uint8_t *block);
uint8_t* encryptBlock(uint8_t *block, uint8_t *keys, const uint8_t rounds);

void encryptAES(uint8_t *bytes, uint8_t *keys, size_t bytecount, size_t cpucount, uint8_t rounds);

#endif
