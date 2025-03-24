#include <stdio.h>
#include <string.h>

// c script to overflow a buffer and see variables inside the stack
// inspired by: https://www.youtube.com/watch?v=e46wHUjNDjE


void vulnerable_function() {

// our key to overflow
// temp exists in our vulnerable function which resides inside the stack during it's execution
// it goes roughly like this inside the memory 

//       NULL
//      (stuff)
//   main function block
//   main function variables
//   return address of vulnerable_function()
//   our temp variable which our ptr points to

    int temp=0;

    int *ptr = &temp;
// counter to see how many pointers we're jumping
    int i = 0;

// for each iteration we go up in the stack 
// i am iterating until the 13th iteration because that's when i reach the main stack
    while(i<13){
// printing values on our way up

    printf("ptr value:%d\n",*ptr);
    i++;

// here we're pointing up by 4 bytes up or sizeof(int)
// note: this won't work the same with an unsigned char or char because of the diffrent sizes
    ptr++;
    
    }
}


int main() {

// the variables we're looking for.
    int a =5 ,b=4 ,c =3;

    vulnerable_function();

    
    return 0;
}
