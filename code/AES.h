#ifndef AES
#define AES

#include <stddef.h>
#include <inttypes.h>


uint8_t * initconstarr(uint8_t * restrict initval);
static void AddRoundKey(uint8_t * restrict bytes, const uint8_t * restrict keys);
static void SubBytes(uint8_t * restrict bytes);
static void ShiftRows(uint8_t * restrict block, uint8_t * restrict tempblock);
static void MixColumns(uint8_t * restrict block, uint8_t * restrict tempblock);
static void encryptBlock(uint8_t * restrict block, uint8_t * restrict tempblock, const uint8_t * restrict keys, const uint8_t rounds);
void encryptBlocks(uint8_t * restrict block, uint8_t * restrict initval, const size_t bytecount, const uint8_t rounds);

void encryptAES(uint8_t *bytes, uint8_t * initval, const size_t bytecount, const size_t cpucount, const uint8_t rounds);

#endif
