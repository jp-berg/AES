#include <stdio.h>
#include <inttypes.h>

void makestuff(uint8_t *arr, size_t length){
    for(size_t i = 0; i < length; i++)
        printf("%c\n", *arr++);
}

void test(void){
    puts("Hello World\n");
}
