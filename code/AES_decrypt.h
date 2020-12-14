#ifndef AES_decrypt
#define AES_decrypt

#include <stddef.h>
#include <inttypes.h>

void testAddRoundKey();
void addRoundKey(uint8_t *block, const uint8_t *keys);
void inverseShiftRows(uint8_t *block);
void inverseSubBytes(uint8_t *block);
void inverseMixColumns(uint8_t *block);
void decryptBlock(uint8_t *block, const uint8_t *keys);


#endif
