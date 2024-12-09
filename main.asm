; Initialize text mode
main:
    ldw a, 1        ; Mode: 1 for text mode
    ldw b, 800      ; Horizontal resolution
    ldw c, 600      ; Vertical resolution
    int 0x70        ; Initialize display
    ldw b, 0        ; Cursor position (character cell index)
    ldw c, 0xFFFFFF ; White color
    

main_loop:
    ; Get key down (handle key press/release)
    mov f, b        ; f <- b
    int 0xF6        ; a <- keycode | b <- first press
    add b, f,       ; b = f + b    ; This moves the value in f back to B, and sence b is eyther 1 or 0, it will eyther increment it, or not increment it. 
    
    str b, 0xEE
    str a, 0xEF
    
    

    ; If a key is not pressed (register 0x1 == 0), continue the loop
    ldw d, 0        ; Check if a key is pressed (if register 0x1 == 1)
    beq a, d, main_loop ; If A == 0, loop back to main_loop (no key is pressed)

    ; Render the character
    int 0x72        ; Render the character (using the keycode from register 0x0 at position b)
    
        ;  Write letter to disk at index   ;push a
        ;  Write letter to disk at index   ;push b
        ;  Write letter to disk at index   ;push c
        ;  Write letter to disk at index   ;push d
        ;  Write letter to disk at index   ;
        ;  Write letter to disk at index   ;ldw a, 8        ; disk number
        ;  Write letter to disk at index   ;ldw b, 0       ; sector number
        ;  Write letter to disk at index   ;ldr c, 0xEE     ; byte offset
        ;  Write letter to disk at index   ;ldr d, 0xEF     ; value to write
        ;  Write letter to disk at index   ;
        ;  Write letter to disk at index   ;int 0x81        ; Write
        ;  Write letter to disk at index   ;
        ;  Write letter to disk at index   ;pop d
        ;  Write letter to disk at index   ;pop c
        ;  Write letter to disk at index   ;pop b
        ;  Write letter to disk at index   ;pop a
    ; Reset cursor to the top of the screen
    jmp main_loop   ; Jump back to the main loop
