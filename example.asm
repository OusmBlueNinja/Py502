; 0x00 -> print register a as char
; 0x01 -> print register a as int
;
; 0xFF -> Halt
; 0xFE -> Error Interupt
; 0xF6 -> put keycode of currently pressed key in A register
;         and but a value (bool)(0 or 1) into b register to
;         indicate whether it is the first time this key has been 
;         pressed.
;
;
; 0x70 -> Init graphics, 
;         (A) mode
;         (B) X resolution
;         (C) Y Resulution
; 0x71 -> Set Pixel, (bitmap mode)
;         (A) Color (0x000000 to 0xFFFFFF)
;         (B) x position
;         (C) y position
; 0x72 -> Set Char, (Text Mode)
;         (A) Character Code
;         (B) Cursor Position 
;         (C) Color (0x000000 to 0xFFFFFF)
;
;
;  ! ALLL FILESYSTEM DRIVE NUMBER ARE LOCAL FILES !
;  drive( drive number (0 to 9)).bin
;  "drive8.bin"
;
;  drive number  -> ( 0 to 9 )
;  sector number -> ( 0 to 15 )
;  byte offset   -> ( 0 to 254 )

;
; 0x80 -> read byte from disk
;         (A) drive number
;         (B) sector number 
;         (C) byte offset
;         moves output to A register
; 0x81 -> write byte from disk
;         (A) drive number
;         (B) sector number 
;         (C) byte offset
;         (D) byte to write



main:
    ldw a, 0xFF     ;  load 255 to A register, Unused
    str a, 0xFF      ;  will cause an error because its writing to program memory
                    ;  You will have to make the address bigger than the program
    int 0x00        ;  interupt to print a register to terminal as a char (debug)
    
    ldw a, 0        ; will be the graphics mode
    str a, 0xF0     ; copy A register to memory address   
    
    ldw a, 800      ; screen width
    str a, 0xF1     ; copy A register to memory address     
    
    ldw a, 600      ; screen height
    str a, 0xF2     ; copy A register to memory address
    jsr init_graphics_mode
    
    
    
init_graphics_mode:
    push a
    push b
    push c
    
    ldr a, 0xF0 ; copy data from memory address to register 'A'
    ldr b, 0xF1 ; copy data from memory address to register 'B'
    ldr c, 0xF2 ; copy data from memory address to register 'C'
    
    int 0x70    ; all interupts in 0x70 - 0x7F are for graphics, 
                ; only 0x70 to 0x72 are implemented
                
    pop c
    pop b
    pop a
    
    ret
