# Py502
a Python CPU emulator with a custom instruction set, and an ASM compiler
## What Doin'?

I am currently working on a C compiler for this custom CPU architecture.
I am also going to add characters to my ASM compiler so you can do stuff like
```asm
message:
  .asciiz db "Hello, World!", 0x00 ; null terminated
```


## Problem??


I've included a broken ASM program, try to fix it with the error messages from the compiler, and let me know where i can improve the messages


```asm

main:
    ldw a, 0xFF     ;  load 255 to A register, Unused
    str a, 0x0F      ;  will cause an error because its writing to program memory
                    ;  You will have to make the address bigger than the program
    int 0x00        ;  interupt to print a register to terminal as a char (debug)
    
    ldw a, 0        ; will be the graphics mode
    str a, 0xF0     ; copy A register to memory address   
    
    ldw a, 800      ; screen width
    str a, 0xF1     ; copy A register to memory address     
    
    ldw a, 600      ; screen height
    str a, 0xF2     ; copy A register to memory address
    jsr _init_graphics_mode
    
    
    
init_graphics_mode:
    push a
    push b
    push c
    
    ldw g, 0xFF ; This is never used
    
    ldr a, 0xF0 ; copy data from memory address to register 'A'
    ldr b, 0xF1 ; copy data from memory address to register 'B'
    ldr c, 0xF2 ; copy data from memory address to register 'C'
    
    int 0x70    ; all interupts in 0x70 - 0x7F are for graphics, 
                ; only 0x70 to 0x72 are implemented
                
    pop b
    pop a
    
    ret

```


## Interupts


0x00 -> print register a as char
0x01 -> print register a as int
0xFF -> Halt
0xFE -> Error Interupt
0xF6 -> put keycode of currently pressed key in A register
        and but a value (bool)(0 or 1) into b register to
        indicate whether it is the first time this key has been 
        pressed.
0x70 -> Init graphics, 
        (A) mode
        (B) X resolution
        (C) Y Resulution
0x71 -> Set Pixel, (bitmap mode)
        (A) Color (0x000000 to 0xFFFFFF)
        (B) x position
        (C) y position
0x72 -> Set Char, (Text Mode)
        (A) Character Code
        (B) Cursor Position 
        (C) Color (0x000000 to 0xFFFFFF)

 ! ALLL FILESYSTEM DRIVE NUMBER ARE LOCAL FILES !
 drive( drive number (0 to 9)).bin
 "drive8.bin"
 drive number  -> ( 0 to 9 )
 sector number -> ( 0 to 15 )
 byte offset   -> ( 0 to 254 )

0x80 -> read byte from disk
         (A) drive number
         (B) sector number 
         (C) byte offset
         moves output to A register
0x81 -> write byte from disk
        (A) drive number
        (B) sector number 
        (C) byte offset
        (D) byte to write


        
## Example error messages for the ASM Compiler
![image](https://github.com/user-attachments/assets/f50d5d51-dfb8-46a8-b3e3-c762d033c2f1)
![image](https://github.com/user-attachments/assets/fd7f2477-a4c6-46c3-afb9-9d47c5daa159)
