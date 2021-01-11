#include "AES.h"
#include <omp.h>
#include <string.h>
#include <stdio.h>

//avoid multiple memcpy, global to local, local functions static, loop countdown for(i = 16; i--; ), loop unrolling, macros, restrict, size of loop-index == size of pointer



static uint8_t sbox[256];
static uint8_t gal_mult_lookup[3][256];

uint8_t * initconstarr(uint8_t * restrict initval)
{
    for(size_t i = 0; i < 256; i++)
    {
        sbox[i] = *initval++;
    }
    for(size_t i = 0; i < 3; i++)
    {
        for(size_t j = 0; j < 256; j++)
        {
            gal_mult_lookup[i][j] = *initval++;
        }
    }
    
    return initval;
}

void pb(char *r,const uint8_t *block){
    printf("\n\n Round %s:", r);
    for(uint8_t i = 0; i < 16; i++)
        printf("%x ", block[i]);
    puts("\n");    
}

inline static void AddRoundKey(uint8_t * restrict bytes, const uint8_t * restrict keys)
{
    for(uint8_t i = 0; i < 16; i++)
    {
        bytes[i] ^= keys[i];
    }
}

inline static void SubBytes(uint8_t * restrict bytes)
{
    for(uint8_t i = 0; i < 16; i++)
    {
        bytes[i] = sbox[bytes[i]];
    }
    
}
    

static void ShiftRows(uint8_t * restrict block, uint8_t * restrict tempblock)
{
    memcpy(tempblock, block, 16 * sizeof(uint8_t));
    
    block[1] = tempblock[5];
    block[2] = tempblock[10];
    block[3] = tempblock[15];
    block[5] = tempblock[9];
    block[6] = tempblock[14];
    block[7] = tempblock[3];
    block[9] = tempblock[13];
    block[10] = tempblock[2];
    block[11] = tempblock[7];
    block[13] = tempblock[1];
    block[14] = tempblock[6];
    block[15] = tempblock[11];
}

static void MixColumns(uint8_t * restrict block, uint8_t * restrict tempblock)
{
    memcpy(tempblock, block, 16 * sizeof(uint8_t));

    for(uint8_t i = 0; i < 16; i += 4)
    {
     
        block[i] = gal_mult_lookup[1][tempblock[i]] ^ 
                   gal_mult_lookup[2][tempblock[i+1]] ^ 
                   gal_mult_lookup[0][tempblock[i+2]] ^ 
                   gal_mult_lookup[0][tempblock[i+3]];
        
        block[i+1] = gal_mult_lookup[0][tempblock[i]] ^ 
                     gal_mult_lookup[1][tempblock[i+1]] ^ 
                     gal_mult_lookup[2][tempblock[i+2]] ^ 
                     gal_mult_lookup[0][tempblock[i+3]];
        
        block[i+2] = gal_mult_lookup[0][tempblock[i]] ^ 
                     gal_mult_lookup[0][tempblock[i+1]] ^ 
                     gal_mult_lookup[1][tempblock[i+2]] ^ 
                     gal_mult_lookup[2][tempblock[i+3]];
        
        block[i+3] = gal_mult_lookup[2][tempblock[i]] ^ 
                     gal_mult_lookup[0][tempblock[i+1]] ^ 
                     gal_mult_lookup[0][tempblock[i+2]] ^ 
                     gal_mult_lookup[1][tempblock[i+3]];
    }
}
                    

static void encryptBlock(uint8_t * restrict block, uint8_t * restrict tempblock, const uint8_t * restrict keys, const uint8_t rounds)
{

    uint8_t ikeys = 0;
    AddRoundKey(block, keys);
    ikeys += 16;
                
    for(uint8_t i = 0; i < rounds - 1; i++)
    {   
        SubBytes(block);
        ShiftRows(block, tempblock);
        MixColumns(block, tempblock);
        AddRoundKey(block, &keys[ikeys]);
        ikeys += 16;
        
    }
    
    SubBytes(block);
    ShiftRows(block, tempblock);
    AddRoundKey(block, &keys[ikeys]);

}

void encryptBlocks(uint8_t * restrict bytes, uint8_t * restrict initval, const size_t bytecount, const uint8_t rounds)
{   
    const uint8_t * keys = initconstarr(initval);
    uint8_t tempblock[16];
    
    for(size_t i = 0; i < bytecount; i += 16)
    {
        encryptBlock(&bytes[i], tempblock, keys, rounds);
    }
}


    
// void encryptAES(uint8_t *bytes, uint8_t * initval, const size_t bytecount, const size_t cpucount, const uint8_t rounds)
// {   
//     
//     size_t chunk = (size_t) (bytecount / cpucount);
//     size_t i;
// #pragma omp parallel num_threads(4)
//     {
// #pragma omp for
//     for(i = 0; i < bytecount; i += chunk)  //TODO: Play with Blockwidth
//     {
//         encryptBlocks(&bytes[i], keys, chunk, rounds);
// //         printf("chunk: %lu\n", i);
//     }
//     encryptBlocks(&bytes[i], keys, bytecount%chunk, rounds);
//     }
//     

// }


    
        
        

    
    
    
    
    

