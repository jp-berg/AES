#ifndef AES
#define AES

#include <stddef.h>
#include <inttypes.h>

static void genMultLookup(uint8_t multlookup[3][256]);

static void AddRoundKey(uint8_t *bytes, const uint8_t *keys);
static void SubBytes(uint8_t *bytes);
static void ShiftRows(uint8_t *block, uint8_t *tempblock);
static void MixColumns(uint8_t *block, uint8_t *tempblock);
static void encryptBlock(uint8_t *block, uint8_t *tempblock, const uint8_t *keys, const uint8_t rounds);
void encryptBlocks(uint8_t *block, const uint8_t *keys, const size_t bytecount, const uint8_t rounds);

void encryptAES(uint8_t *bytes, const uint8_t *keys, const size_t bytecount, const size_t cpucount, const uint8_t rounds);

#endif
