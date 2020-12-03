//const char sbox[255] = {0x63, 0x7c

#include <stdint.h>
#include <stdio.h>

#define ROTL8(x,shift) ((uint8_t) ((x) << (shift)) | ((x) >> (8 - (shift))))

void initialize_aes_sbox(uint8_t sbox[256]) {
	uint8_t p = 1, q = 1;
	
	/* loop invariant: p * q == 1 in the Galois field */
	do {
		/* multiply p by 3 */
		p = p ^ (p << 1) ^ (p & 0x80 ? 0x11B : 0);

		/* divide q by 3 (equals multiplication by 0xf6) */
		q ^= q << 1;
		q ^= q << 2;
		q ^= q << 4;
		q ^= q & 0x80 ? 0x09 : 0;

		/* compute the affine transformation */
		uint8_t xformed = q ^ ROTL8(q, 1) ^ ROTL8(q, 2) ^ ROTL8(q, 3) ^ ROTL8(q, 4);

		sbox[p] = xformed ^ 0x63;
	} while (p != 1);

	/* 0 is a special case since it has no inverse */
	sbox[0] = 0x63;
}

void genMultLookup(uint8_t multlookup[3][256])
{
    uint8_t temp;
    for(size_t i = 0; i < 256; i++){
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


main(){
    FILE *file;
    uint8_t box[256];
    initialize_aes_sbox(box);
    file = fopen("Code.txt", "w");
    for(int i = 0; i < 0x10; i++){
        for(int j = 0; j < 0x10; j++){
            fprintf(file, "0x%x, ", box[(i*0x10)+j]);
        }
        fprintf(file, "\n");
    }
    fclose(file);
}
