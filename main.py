import pygame, time, os

class CPU:
    def __init__(self, memory_size=256):
        stack_size = 32
        self.memory = [0] * memory_size  # Fixed-size memory
        self.stack = [0] * stack_size
        self.SP = len(self.stack)  # Stack grows downward
        self.PC = 0x00  # Program Counter
        self.A = 0 # Register A
        self.B = 0 # Register B
        self.C = 0 # Register C
        self.D = 0 # Register D
        self.E = 0 # Register E   
        self.F = 0 # Register F 
        
        self.running = True
        
        self.cycles = 0
        
        # Initialize pygame screen for 256x256 resolution
        self.V_res = -1
        self.H_res = -1
        self.screen = None
        
        self.keydown = False
        self.last_key = None
        
        
        self.text_buffer = None  # Space and white color

        
        
        
    def state(self):
        # Print Registers in Hex Format
        print("Registers:")
        print(f"   A: 0x{self.A:02X}")
        print(f"   B: 0x{self.B:02X}")
        print(f"   C: 0x{self.C:02X}")
        print(f"   D: 0x{self.D:02X}")
        print(f"   E: 0x{self.E:02X}")
        print(f"   F: 0x{self.F:02X}")
        
        # Print Stack (if needed, in a similar hex format)
        print("\nStack:")
        print(self.stack)
        
        # Print Total Cycles
        print(f"\nTotal Cycles: {self.cycles}")
        
        # Print Memory in Hex, with addresses on the left and values aligned
        print("\nMemory:")
        i = 0
        for address in range(0, len(self.memory), 16):  # Iterate by 16 values (one row at a time)
            # Print address
            print(f"0x{address:04X}: ", end="")  # Print the memory address in hex (4 digits)
            
            # Print 16 values on the same line
            for j in range(16):
                if address + j < len(self.memory):  # Avoid out-of-bounds
                    print(f"{self.memory[address + j]:02X}", end=" ")
                else:
                    print("   ", end=" ")  # Empty spaces for remaining uninitialized memory
            print()  # Move to the next line
    
    

    def load_program(self, program):
        """Load the machine code program into memory."""
        self.memory[:len(program)] = program
        

    def fetch(self):
        """Fetch the next instruction."""
        if self.PC >= len(self.memory):
            self.running = False
            return None
        
        # Check for 4-byte instructions
        opcode = self.memory[self.PC]
        length = 4 if opcode in (0x08, 0x09) else 3
        instruction = self.memory[self.PC:self.PC + length]
        
        if len(instruction) < length:
            instruction += [0] * (length - len(instruction))
        
        self.PC += length
        return instruction



    def execute(self, instruction):
        self.cycles+=1
        #print(self.PC)
        """Execute an instruction."""
        if instruction is None:
            return

        opcode = instruction[0]
        if opcode == 0x00:  # Halt
            self.running = False
        elif opcode == 0x01:  # LOAD
            reg, value = instruction[1], instruction[2]
            self._load(reg, value)
        elif opcode == 0x02:  # MOV
            dest, src = instruction[1], instruction[2]
            self._mov(dest, src)
        elif opcode == 0x03:  # ADD
            dest, src = instruction[1], instruction[2]
            self._add(dest, src)
        elif opcode == 0x04:  # SUB
            dest, src = instruction[1], instruction[2]
            
            self._sub(dest, src)
            
        elif opcode == 0x05:  # STORE
            reg, addr = instruction[1], instruction[2]
            self._store(reg, addr)
        elif opcode == 0x06:  # LOADM
            reg, addr = instruction[1], instruction[2]
            self._loadm(reg, addr)
        elif opcode == 0x08:  # BNE (Branch if Not Equal)
            reg, reg2, target = instruction[1], instruction[2], instruction[3]
            self._bne(reg, reg2, target)
        elif opcode == 0x09:  # beq (Branch if Equal)
            reg, reg2, target = instruction[1], instruction[2], instruction[3]
            self._beq(reg, reg2, target)
        elif opcode == 0x0A:  # int interupt handler
            value, opt = instruction[1], instruction[2]
            self._int(value, opt)
        elif opcode == 0x0B:  # push stack
            reg, opt = instruction[1], instruction[2]
            self._push(reg, opt)
            
        elif opcode == 0x0C:  # pop stack
            reg, opt = instruction[1], instruction[2]
            self._pop(reg, opt)
        elif opcode == 0x0D:  # pop stack
            value, opt = instruction[1], instruction[2]
            self._jsr(value, opt)
        elif opcode == 0x0E:  # pop stack
            value, opt = instruction[1], instruction[2]
            self._ret(value, opt)
        
        elif opcode == 0x0F:  # xor
            reg, reg2 = instruction[1], instruction[2]
            self._xor(reg, reg2)
            
        elif opcode == 0x10:  # and
            reg, reg2 = instruction[1], instruction[2]
            self._and(reg, reg2)
            
        elif opcode == 0x11:  # jmp
            addr, opt = instruction[1], instruction[2]
            self._jmp(addr, opt)
        
        elif opcode == 0x12:  # mul
            reg1, reg2 = instruction[1], instruction[2]
            self._mul(reg1, reg2)
            
        elif opcode == 0x13:  # div
            reg1, reg2 = instruction[1], instruction[2]
            self._div(reg1, reg2)
            
        elif opcode == 0x14:  # beq (Branch if Equal)
            reg, reg2, target = instruction[1], instruction[2], instruction[3]
            self._blt(reg, reg2, target)
        
        else:
            raise ValueError(f"Unknown opcode: {opcode}")



    def _mul(self, reg1, reg2):
        result = self._get_register(reg1) * self._get_register(reg2)
        self._set_register(reg1, result)
        
    def _div(self, reg1, reg2):
        a = int(self._get_register(reg1))
        b = int(self._get_register(reg2))
        if b == 0:
            raise ZeroDivisionError("Divided by 0")
        result = a / b
        self._set_register(reg1, result)
        
        
    def _xor(self, reg, reg2):
        # Retrieve values from the registers, ensuring they're integers
        val1 = int(self._get_register(reg))
        val2 = int(self._get_register(reg2))
        # Perform XOR operation
        result = val1 ^ val2
    
        # Ensure the result is also an integer and set it back to the register
        self._set_register(reg, result)
        
    def _and(self, reg, reg2):
        result = self._get_register(reg) & self._get_register(reg2)
        self._set_register(reg, result)
        
    
    def _load(self, reg, value):
        if reg == 0x00:
            self.A = value
        elif reg == 0x01:
            self.B = value
        elif reg == 0x02:
            self.C = value
        elif reg == 0x03:
            self.D = value
        elif reg == 0x04:
            self.E = value
        elif reg == 0x05:
            self.F = value
        else:
            raise ValueError("Invalid register.")
            
    def _push(self, reg, opt):
        self.SP -= 1
        if self.SP < 0:
            #print(f"STACK OVERFLOW: SP={self.SP}")
            raise OverflowError("Stack overflow")
        val = self._get_register(reg)
        self.stack[self.SP] = val
        #print(f"PUSH: SP={self.SP}, VALUE={val}, STACK={self.stack}")
    
    def _pop(self, reg, opt):
        if self.SP >= len(self.stack):
            #print(f"STACK UNDERFLOW: SP={self.SP}")
            raise OverflowError("Stack underflow")
        val = self.stack[self.SP]
        self.stack[self.SP] = 0
        self.SP += 1
        self._set_register(reg, val)
        #print(f"POP: SP={self.SP}, VALUE={val}, STACK={self.stack}")

    def _jsr(self, value, opt):
        self.SP -= 1
        if self.SP < 0:
            #print(f"STACK OVERFLOW: SP={self.SP}")
            raise OverflowError("Stack overflow")
        self.stack[self.SP] = self.PC+3
        self.PC = value
        #print(f"JSR: SP={self.SP}, PC={self.PC}, STACK={self.stack}")
        
    def _jmp(self, value, opt):
        self.PC = value
        
    
    
    def _ret(self, value, opt):
        if self.SP >= len(self.stack):
            #print(f"STACK UNDERFLOW: SP={self.SP}")
            raise OverflowError("Stack underflow")
        address = self.stack[self.SP]
        self.stack[self.SP] = 0
        self.SP += 1
        self.PC = address
        #print(f"RET: SP={self.SP}, PC={self.PC}, STACK={self.stack}")
    
        
        
    
    def _display_init(self):
        mode = self._get_register(0x0)
        x = self._get_register(0x1)
        y = self._get_register(0x2)
    
        self.V_res = y
        self.H_res = x
        self.mode = mode  # Save the display mode
    
        pygame.init()
    
        if mode == 0:  # Bitmap mode
            self.screen = pygame.display.set_mode((x, y))
            self.screen.fill((0, 0, 0))  # Black background
            pygame.display.set_caption("Bitmap Mode")
        elif mode == 1:  # Text mode
            self.cell_width = 10  # Width of each text cell (in pixels)
            self.cell_height = 16  # Height of each text cell (in pixels)
            self.max_columns = self.H_res // self.cell_width
            self.max_rows = self.V_res // self.cell_height
    
            # Initialize the text buffer
            self.text_buffer = [[(0x20, 0xFFFFFF) for _ in range(self.max_columns)] for _ in range(self.max_rows)]
            
            self.font = pygame.font.Font(pygame.font.get_default_font(), self.cell_height)
            self.screen = pygame.display.set_mode((x, y))
            self.screen.fill((0, 0, 0))  # Black background
            pygame.display.set_caption("Text Mode")
        else:
            raise ValueError("Invalid display mode")
    
    
    
        
        
            
    def _int(self, value, opt):
        
        #? Display Interrupts
        if value == 0x70:  # Init display
            self._display_init()
        elif value == 0x71:  # Set pixel (bitmap mode)
            self._set_pixel()
        elif value == 0x72:  # Render character (text mode)
            self._add_text()
        
        #? Terminal Interrupts
        elif value == 0x00:  # Print character
            self._print_register_char()
        elif value == 0x01:  # Print integer
            self._print_register_int()
        
        #? System Interrupts
        elif value == 0xFF:  # Halt
            self.running = False
            return
        elif value == 0xF6:  # Get key down
            keys = pygame.key.get_pressed()  # Get the state of all keys
            
            key_pressed = False  # Flag to check if a key was pressed in this cycle
            current_key = None  # Track the currently detected key
        
            for keycode in range(len(keys)):
                if keys[keycode]:  # If this key is pressed
                    current_key = keycode  # Set the current key
                    
                    self._set_register(0x0, keycode)  # Set register A to the keycode
        
                    if not self.keydown or (self.last_key != current_key):  
                        # If it's the first press or a new key is pressed
                        self._set_register(0x1, 1)  # Set register B to indicate a new key press
                        self.keydown = True  # Mark that a key is pressed
                        self.last_key = current_key  # Update the last pressed key
                    else:
                        # If the same key is still being held
                        self._set_register(0x1, 0)  # Set register B to indicate no new key
                    key_pressed = True
                    return
        
            if not key_pressed:  # If no key is pressed (key release)
                self._set_register(0x0, 0)  # Set register A to 0 (no key pressed)
                self._set_register(0x1, 0)  # Set register B to 0 (reset key state)
                self.keydown = False  # Reset the keydown flag
                self.last_key = None  # Clear the last pressed key
        


        
        
        elif value == 0xFE:  # Error interrupt
            print("Error interrupt")
            print(f"Register A: {self._get_register(0)}")
            print(f"Register B: {self._get_register(1)}")
            print(f"Register C: {self._get_register(2)}")
            self.running = False 
            
            
            
        elif value == 0x80:  # Read byte from disk
            self._read_byte_from_disk(opt)
            
        elif value == 0x81:  # Read byte from disk
            self._write_byte_from_disk(opt)
            
            
        
        else:
            raise ValueError(f"Unknown interrupt: {value}")
    
    def _read_byte_from_disk(self, opt):
        # Register layout:
        # a = drive number (0-9)
        # b = sector number (0-15)
        # c = byte offset within sector (0-254)
        
        drive_number = self._get_register(0x0)  # Drive number
        sector_number = self._get_register(0x1)  # Sector number
        byte_offset = self._get_register(0x2)  # Byte offset within sector
    
        # Validate input values and trigger error interrupt if invalid
        if not (0 <= drive_number <= 9):
            self._set_register(0x0, 0x81)  # Error code 1: Invalid drive number
            self._set_register(0x1, self.PC)  # Set current PC to register 0xB
            self._set_register(0x2, 0)  # Set register 0xC to 0 as specified
            self._int(0xFE, 0)  # Trigger the error interrupt
            return
    
        if not (0 <= sector_number <= 15):
            self._set_register(0x0, 0x82)  # Error code 2: Invalid sector number
            self._set_register(0x1, self.PC)
            self._set_register(0x2, 0)
            self._int(0xFE, 0)
            return
    
        if not (0 <= byte_offset <= 254):
            self._set_register(0x0, 0x83)  # Error code 3: Invalid byte offset
            self._set_register(0x1, self.PC)
            self._set_register(0x2, 0)
            self._int(0xFE, 0)
            return
        
        # Construct the disk file path (e.g., "disk0.bin", "disk1.bin")
        disk_file = f"disk{drive_number}.bin"
        
        if not os.path.exists(disk_file):
            self._set_register(0x0, 0x84)  # Error code 4: Disk file not found
            self._set_register(0x1, self.PC)
            self._set_register(0x2, 0)
            self._int(0xFE, 0)
            return
    
        # Open the disk file and read the desired byte
        with open(disk_file, 'rb') as f:
            # Calculate the position to read from: 
            # (sector_number * 255 bytes per sector) + byte_offset
            position = (sector_number * 255) + byte_offset
            f.seek(position)
            
            byte_value = f.read(1)  # Read one byte
            if len(byte_value) == 0:
                self._set_register(0x0, 0x85)  # Error code 5: Failed to read byte
                self._set_register(0x1, self.PC)
                self._set_register(0x2, 0)
                self._int(0xFE, 0)
                return
    
        # Store the byte value in a register (0x4 for this example)
        self._set_register(0x4, byte_value[0])  # Store byte in register 0x4
        #print(f"Read byte: {byte_value[0]:#04x} from {disk_file}, sector {sector_number}, byte {byte_offset}")
        
    def _write_byte_from_disk(self, opt):
        # Register layout:
        # a = drive number (0-9)
        # b = sector number (0-15)
        # c = byte offset within sector (0-254)
        # d = byte value to write (0-255)
        
        drive_number = self._get_register(0x0)  # Drive number
        sector_number = self._get_register(0x1)  # Sector number
        byte_offset = self._get_register(0x2)  # Byte offset within sector
        byte_to_write = self._get_register(0x3)  # Byte to write
        
    
        # Validate input values and trigger error interrupt if invalid
        if not (0 <= drive_number <= 9):
        
            self._set_register(0x0, 0x81)  # Error code 1: Invalid drive number
            self._set_register(0x1, self.PC)  # Set current PC to register 0xB
            self._set_register(0x2, 0)  # Set register 0xC to 0 as specified
            self._int(0xFE, 0)  # Trigger the error interrupt
            return
    
        if not (0 <= sector_number <= 15):
            
            self._set_register(0x0, 0x82)  # Error code 2: Invalid sector number
            self._set_register(0x1, self.PC)
            self._set_register(0x2, 0)
            self._int(0xFE, 0)
            return
    
        if not (0 <= byte_offset <= 254):   
            self._set_register(0x0, 0x83)  # Error code 3: Invalid byte offset
            self._set_register(0x1, self.PC)
            self._set_register(0x2, 0)
            self._int(0xFE, 0)
            return
    
        # Construct the disk file path (e.g., "disk0.bin", "disk1.bin")
        disk_file = f"drive{drive_number}.bin"
        
        if not os.path.exists(disk_file):
            print(0x84)
            self._set_register(0x0, 0x84)  # Error code 4: Disk file not found
            self._set_register(0x1, self.PC)
            self._set_register(0x2, 0)
            self._int(0xFE, 0)
            return
        
        # Open the disk file in 'r+b' mode for reading and writing
        with open(disk_file, 'r+b') as f:
            # Calculate the position to write to: 
            # (sector_number * 255 bytes per sector) + byte_offset
            position = (sector_number * 255) + byte_offset
            f.seek(position)  # Move the file pointer to the desired position
            
            # Write the byte to the file
            f.write(bytes([byte_to_write]))  # Write a single byte to the file
        #print(f"Written byte: {byte_to_write:#04x} to {disk_file}, sector {sector_number}, byte {byte_offset}")
    

            
    def _print_register_char(self):
    
        char = self._get_register(0x0)
        print(chr(char))
    def _print_register_int(self):
    
        char = self._get_register(0x0)
        print(char)

    def _mov(self, dest, src):
        value = self._get_register(src)
        self._set_register(dest, value)

    def _add(self, dest, src):
        result = self._get_register(dest) + self._get_register(src)
        self._set_register(dest, result)

    def _sub(self, dest, src):
    
        result = self._get_register(dest) - self._get_register(src)
        
        self._set_register(dest, result)

    def _store(self, reg, addr):
        if addr < 0 or addr >= len(self.memory):
            raise ValueError("Invalid memory address.")
        self.memory[addr] = self._get_register(reg)
        
        

    def _loadm(self, reg, addr):
        if addr < 0 or addr >= len(self.memory):
            raise ValueError("Invalid memory address.")
        value = self.memory[addr]
        self._set_register(reg, value)
        
        
    def _set_pixel(self):
        if not self.screen or self.mode != 0:  # Ensure it's bitmap mode
            return  

        _color = self._get_register(0)
        _x = self._get_register(1)
        _y = self._get_register(2)  

        if 0 <= _x < self.H_res and 0 <= _y < self.V_res:
            r = (_color & 0xFF0000) >> 16
            g = (_color & 0x00FF00) >> 8
            b = (_color & 0x0000FF)
            self.screen.set_at((_x, _y), (r, g, b))
        else:
            raise ValueError("Pixel coordinates out of bounds") 
    
    
    
    def _add_text(self):
        if not self.screen or self.mode != 1:  # Ensure it's text mode
            return
    
        # Retrieve registers
        _char = self._get_register(0) & 0xFF  # ASCII character
        _cursor_pos = self._get_register(1)  # Current cursor position (in terms of character cells)
        _color = self._get_register(2)  # Text color
    
        # Ensure cursor position is within bounds
        if _cursor_pos >= self.max_columns * self.max_rows:
            _cursor_pos = (self.max_columns * self.max_rows) - 1
    
        # Calculate row and column from the cursor position
        cursor_x = _cursor_pos % self.max_columns
        cursor_y = _cursor_pos // self.max_columns
    
        # Update the text buffer
        self.text_buffer[cursor_y][cursor_x] = (_char, _color)
    
        # Redraw the entire screen
        self.screen.fill((0, 0, 0))  # Clear the screen
        for row_index, row in enumerate(self.text_buffer):
            for col_index, (char, color) in enumerate(row):
                # Convert to pixel coordinates
                _x = col_index * self.cell_width
                _y = row_index * self.cell_height
    
                # Extract color components (RGB)
                r = (color & 0xFF0000) >> 16
                g = (color & 0x00FF00) >> 8
                b = (color & 0x0000FF)
    
                # Render the character
                text_surface = self.font.render(chr(char), True, (r, g, b))
                self.screen.blit(text_surface, (_x, _y))
    
        # Update the display
        pygame.display.flip()
    
    
    
    
    


            
    def _bne(self, reg, reg2, target):
        """Branch to target address if register != value."""
        if self._get_register(reg) != self._get_register(reg2):
            if 0 <= target < len(self.memory):
                self.PC = target
            else:
                raise ValueError(f"Invalid branch target address: {target}")
                
    def _blt(self, reg, reg2, target):
        """Branch to target address if register < value."""
        if self._get_register(reg) < self._get_register(reg2):
            if 0 <= target < len(self.memory):
                self.PC = target
            else:
                raise ValueError(f"Invalid branch target address: {target}")



    def _beq(self, reg, reg2, target):
        """Branch to target address if register == value."""
        if self._get_register(reg) == self._get_register(reg2):
            self.PC = target

    def _get_register(self, reg):
        if reg == 0x00:  # A
            return self.A
        elif reg == 0x01:  # B
            return self.B
        elif reg == 0x02:  # C
            return self.C
        elif reg == 0x03:
            return self.D
        elif reg == 0x04:
            return self.E
        elif reg == 0x05:
            return self.F
        else:
            raise ValueError(f"Invalid register: {reg}")


    def _set_register(self, reg, value):
        if type(value) != int:
            raise TypeError(f"Invalid register type")
        if reg == 0x00:
            self.A = value
        elif reg == 0x01:
            self.B = value
        elif reg == 0x02:
            self.C = value
        elif reg == 0x03:
            self.D = value
        elif reg == 0x04:
            self.E = value
        elif reg == 0x05:
            self.F = value
        else:
            raise ValueError("Invalid register code.")

    def run(self):
        """Run the loaded program with error interrupts."""
        line = 0
        timer = 0
        try:
            end = time.time()
            start = time.time()
            while self.running:
                start = time.time()
    
                instruction = self.fetch()
                #print(instruction)
    
                if self.screen:
                    if timer >= 1 / 60:
                        pygame.display.update() 
                        timer = 0
    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
    
                self.execute(instruction)
                line += 1
                end = time.time()
                timer += end - start
    
        except ValueError as e:
            print(e, self.B, self.C)
            # Trigger an error interrupt with details
            self._set_register(0x0, 0x1) # Error Type
            self._set_register(0x1, self.PC) # Error Address
            self._set_register(0x2, instruction[0]) # Error Type
            
            self._int(0xFE, 0)
        except IndexError as e:
            print(e, self.B, self.C)
            # Trigger an error interrupt with details
            self._set_register(0x0, 0x2) # Error Type
            self._set_register(0x1, self.PC) # Error Address
            self._set_register(0x2, instruction[0]) # Error Type
            
            self._int(0xFE, 0)
        except OverflowError as e:
            print(e, self.B, self.C)
            # Trigger an error interrupt with details
            self._set_register(0x0, 0x3) # Error Type
            self._set_register(0x1, self.PC) # Error Address
            self._set_register(0x2, instruction[0]) # Error Type
            
            self._int(0xFE, 0)
            
        except ZeroDivisionError as e:
            print(e, self.B, self.C)
            # Trigger an error interrupt with details
            self._set_register(0x0, 0x4) # Error Type
            self._set_register(0x1, self.PC) # Error Address
            self._set_register(0x2, instruction[0]) # Error Type
            
            self._int(0xFE, 0) # call error interrupt
            
        #ValueError, IndexError, OverflowError
        
            


program = [1, 0, 1, 1, 1, 800, 1, 2, 600, 10, 112, 0, 1, 1, 0, 1, 2, 16777215, 2, 5, 1, 10, 246, 0, 3, 1, 5, 5, 1, 238, 5, 0, 239, 1, 3, 0, 9, 0, 3, 18, 10, 114, 0, 11, 0, 0, 11, 1, 0, 11, 2, 0, 11, 3, 0, 1, 0, 8, 1, 1, 0, 6, 2, 238, 6, 3, 239, 10, 129, 0, 12, 3, 0, 12, 2, 0, 12, 1, 0, 12, 0, 0, 17, 18, 0]






# Initialize CPU, load program, and run
cpu = CPU()
cpu.load_program(program)
cpu.run()


cpu.state()