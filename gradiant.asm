main:
    jsr lcd_init      ; Initialize the screen
    ldw b, 0          ; Initialize register b (x position)
    ldw c, 0          ; Initialize register c (y position)
    ldw d, 1          ; Increment value
    ldw f, 600        ; Screen width/height limit
    
    ; Store scaling factors in memory (safe zone past 0xC8)
    ldw a, 0x0   ; Scaling factor for green (shift left by 8 bits)
    str a, 0xD0       ; Store in memory at address 0xD0
    ldw a, 0xFF0000   ; Scaling factor for red (shift left by 16 bits)
    str a, 0xC8       ; Store in memory at address 0xC8
    ldw a, 0x00FF00   ; Scaling factor for green (shift left by 8 bits)
    str a, 0xCC       ; Store in memory at address 0xCC
    

loop:
    ; Compute red channel
    mov a, b          ; Copy x position to a
    ldr e, 0xC8       ; Load red scaling factor
    mul a, e          ; Multiply x by red scaling factor
    
    ; Compute green channel
    mov e, c          ; Copy y position to e
    ldr a, 0xCC       ; Load green scaling factor into a
    mul e, a          ; Multiply y by green scaling factor (result in e)
    
    ; Combine red and green channels
    add a, e          ; Combine red and green channels (result in a)
    
    ; Add blue channel (based on x for simplicity)
    add a, b          ; Blue intensity based on x position
    
    ; Draw the pixel
    int 0x71          ; Set pixel color at (b, c)
    int 0xF6          ; get key pressed
    
    
next:
    ; Update position
    ldw a, 0          ; Reset a
    add b, d          ; Increment x (b += 1)
    bne b, f, loop    ; If b < 256, continue loop
    ldw b, 0          ; Reset x
    add c, d          ; Increment y (c += 1)
    bne c, f, loop    ; If c < 256, continue loop

    ; Halt
    int 0xFF          ; Stop program

lcd_init:
    push a
    push b
    push c
    
    
    ldw a, 0x0        ; mode
    
    ldw b, 256        ; Vertical resolution
    ldw c, 256        ; Horizontal resolution
    int 0x70          ; Initialize screen
    
    pop c
    pop b
    pop a
    ret
