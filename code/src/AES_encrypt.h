#ifndef AES
#define AES

#include <stddef.h>
#include <inttypes.h>


uint8_t * initconstarr(uint8_t * restrict initval);
void AddRoundKey(uint8_t * restrict bytes, const uint8_t * restrict keys);
void SubBytes(uint8_t * restrict bytes, const uint8_t * restrict sbox);
void ShiftRows(uint8_t * restrict block, uint8_t * restrict tempblock);
void MixColumns(uint8_t * restrict block, uint8_t * restrict tempblock, const uint8_t (*restrict gal_mult_lookup)[256]);
void encryptBlock(uint8_t * restrict block, uint8_t * restrict tempblock, const uint8_t * restrict keys, const uint8_t rounds, const uint8_t * restrict sbox, const uint8_t (*restrict gal_mult_lookup)[256]);
void encryptBlocks(uint8_t * restrict block, uint8_t * restrict initval, const size_t bytecount, const uint8_t rounds);

void encryptAES(uint8_t *bytes, uint8_t * initval, const size_t bytecount, const size_t cpucount, const uint8_t rounds);

#endif
