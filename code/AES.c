#include "AES.h"
#include <omp.h>
#include <string.h>
#include <stdio.h>

const uint8_t sbox[256] = 
{   0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x1, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76, 
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15, 
    0x4, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x5, 0x9a, 0x7, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 
    0x9, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 
    0x53, 0xd1, 0x0, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x2, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 
    0xcd, 0xc, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73, 
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0xb, 0xdb, 
    0xe0, 0x32, 0x3a, 0xa, 0x49, 0x6, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x8, 
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x3, 0xf6, 0xe, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 
    0x8c, 0xa1, 0x89, 0xd, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0xf, 0xb0, 0x54, 0xbb, 0x16    };
    
static uint8_t gal_mult_lookup[3][256];

void pb(char *r,const uint8_t *block){
    printf("\n\n Round %s:", r);
    for(uint8_t i = 0; i < 16; i++)
        printf("%x ", block[i]);
    puts("\n");    
}

void genMultLookup(uint8_t multlookup[3][256])
{
    uint8_t temp;
    for(size_t i = 0; i < 256; i++)
    {
        multlookup[0][i] = i;
        
        temp = i & 0x80;
        multlookup[1][i] = i << 1;
        if(temp)
        {
            multlookup[1][i] ^= 0x1b;
        }
            
        multlookup[2][i] = multlookup[1][i] ^ i;
    }
}

void inline AddRoundKey(uint8_t *bytes, const uint8_t *keys)
{
    for(uint8_t i = 0; i < 16; i++)
    {
        bytes[i] ^= keys[i];
    }
}

void inline SubBytes(uint8_t *bytes)
{
    for(uint8_t i = 0; i < 16; i++)
    {
        bytes[i] = sbox[bytes[i]];
    }
}
    

void ShiftRows(uint8_t *block)
{
    uint8_t tempblock[16];
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

void MixColumns(uint8_t *block)
{
    uint8_t tempblock[16];
    memcpy(tempblock, block, 16 * sizeof(uint8_t));
    genMultLookup(gal_mult_lookup);

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
                    

void encryptBlock(uint8_t *block, const uint8_t *keys, const uint8_t rounds)
{

    uint8_t ikeys = 0;
    
    AddRoundKey(block, keys);
    ikeys += 16;
                
    for(uint8_t i = 0; i < rounds - 1; i++)
    {   
        SubBytes(block);
        ShiftRows(block);
        MixColumns(block);
        AddRoundKey(block, &keys[ikeys]);
        ikeys += 16;
        
    }
    
    SubBytes(block);
    ShiftRows(block);
    AddRoundKey(block, &keys[ikeys]);

}

void encryptBlocks(uint8_t *bytes, const uint8_t *keys, const size_t bytecount, const uint8_t rounds){
    for(size_t i = 0; i < bytecount; i += 16)
    {
        encryptBlock(&bytes[i], keys, rounds);
    }
}


    
void encryptAES(uint8_t *bytes, const uint8_t *keys, const size_t bytecount, const size_t cpucount, const uint8_t rounds)
{
    genMultLookup(gal_mult_lookup);
    size_t chunk = (size_t) (bytecount / cpucount);
    printf("chunk: %lu\n", chunk);
    
    size_t i;
#pragma omp parallel num_threads(cpucount)
    {
#pragma omp for
    for(i = 0; i < bytecount; i += chunk)  //TODO: Play with Blockwidth
    {
        puts("HERE\n");
        encryptBlocks(&bytes[i], keys, chunk, rounds);
        //if(i%62500 == 0) printf("Byte %lu of %lu (%lf Prozent)\n", i, bytecount,  100 * ((double)i) / ((double)bytecount));
    }
    }
    printf("i: %lu, bytecount: %lu\n", i, bytecount);
    encryptBlocks(&bytes[i], keys, bytecount - i, rounds);
}


    
        
        

    
    
    
    
    
