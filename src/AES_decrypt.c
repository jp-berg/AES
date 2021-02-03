/*
 * AES_decrypt.c
 *
 * Libary to decrypt full 16-byte block with the AES-algorithm.
 *
 * Author: Simon Keil
 * Year: 2021
 *
 */

#include "AES_decrypt.h"
#include <omp.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>


/* The flipped state matrix for the mix columns step */
const uint8_t state_matrix_flipped[16] = {
      0x0e, 0x0b, 0x0d, 0x09,
      0x09, 0x0e, 0x0b, 0x0d,
      0x0d, 0x09, 0x0e, 0x0b,
      0x0b, 0x0d, 0x09, 0x0e
};


void addRoundKey(uint8_t *block, const uint8_t *keys)
{
    for(uint8_t i = 0; i < 16; i++)
    {
        block[i] ^= keys[i];
    }
}


void inverseShiftRows(uint8_t *block)
{

    uint8_t tmp[16];
    memcpy(tmp, block, 16 * sizeof(uint8_t));
    block[1] = tmp[13];
    block[2] = tmp[10];
    block[3] = tmp[7];
    block[5] = tmp[1];
    block[6] = tmp[14];
    block[7] = tmp[11];
    block[9] = tmp[5];
    block[10] = tmp[2];
    block[11] = tmp[15];
    block[13] = tmp[9];
    block[14] = tmp[6];
    block[15] = tmp[3];
}


void inverseSubBytes(uint8_t *block, const uint8_t *inv_sbox)
{
    for(uint8_t i = 0; i < 16; i++)
    {
        block[i] = inv_sbox[block[i]];
    }
}

//peassants algorithm as per the wikipedia article on finite field arithmatic
uint8_t multiply(uint8_t a, uint8_t b)
{
    uint16_t product = 0;

    for(uint8_t i = 0; i < 8; i++)
    {
        if((b & 1) != 0)
            product ^= a;
        b = b >> 1;
        bool carry = ((a & 0x80) != 0);
        a = a << 1;
        if(carry)
            a ^= 0x1B;
    }

    return product;
}


void inverseMixColumns(uint8_t *block)
{
    uint8_t tmp[16];
    memcpy(tmp, block, 16 * sizeof(uint8_t));

    for(uint8_t i = 0; i < 16; i+=4) {
        block[i] = multiply(tmp[i], state_matrix_flipped[0]) ^
                   multiply(tmp[i+1], state_matrix_flipped[1]) ^
                   multiply(tmp[i+2], state_matrix_flipped[2]) ^
                   multiply(tmp[i+3], state_matrix_flipped[3]);
        block[i+1] = multiply(tmp[i], state_matrix_flipped[4]) ^
                   multiply(tmp[i+1], state_matrix_flipped[5]) ^
                   multiply(tmp[i+2], state_matrix_flipped[6]) ^
                   multiply(tmp[i+3], state_matrix_flipped[7]);
        block[i+2] = multiply(tmp[i], state_matrix_flipped[8]) ^
                   multiply(tmp[i+1], state_matrix_flipped[9]) ^
                   multiply(tmp[i+2], state_matrix_flipped[10]) ^
                   multiply(tmp[i+3], state_matrix_flipped[11]);
        block[i+3] = multiply(tmp[i], state_matrix_flipped[12]) ^
                   multiply(tmp[i+1], state_matrix_flipped[13]) ^
                   multiply(tmp[i+2], state_matrix_flipped[14]) ^
                   multiply(tmp[i+3], state_matrix_flipped[15]);

    }
}


void decryptBlock(uint8_t *block, const uint8_t *keys, const uint8_t *inv_sbox)
{
    // Round without mixcolumns
    addRoundKey(block, &keys[16*10]);

    // full rounds
    for(uint8_t i = 9; i > 0; i--)
    {
        inverseShiftRows(block);
        inverseSubBytes(block, inv_sbox);
        addRoundKey(block, &keys[16*i]);
        inverseMixColumns(block);
    }

    // one additional key-addition
    inverseShiftRows(block);
    inverseSubBytes(block, inv_sbox);
    addRoundKey(block, &keys[0]);
}


void decryptBlocks(uint8_t *bytes, const uint8_t *keys, const size_t length,
                    const uint8_t *inv_sbox)
{
    for(size_t i = 0; i < length; i += 16)
    {
        decryptBlock(&bytes[i], keys, inv_sbox);
    }
}
