#ifndef AES_decrypt
#define AES_decrypt

#include <stddef.h>
#include <inttypes.h>

void testAddRoundKey();
void addRoundKey(uint8_t *block, const uint8_t *keys);
void inverseShiftRows(uint8_t *block);
void inverseSubBytes(uint8_t *block, const uint8_t *inv_sbox);
uint8_t multiply(uint8_t a, uint8_t b);
void inverseMixColumns(uint8_t *block);
void decryptBlock(uint8_t *block, const uint8_t *keys, const uint8_t *inv_sbox);
void decryptBlocks(uint8_t *block, const uint8_t *keys, const size_t length,
                    const uint8_t *inv_sbox);


#endif
