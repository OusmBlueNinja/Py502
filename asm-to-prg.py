
import re
from termcolor import colored

filename = "main.asm"

with open(filename,"r") as f:
    lines = f.readlines()



def convert_to_int(value):
    if isinstance(value, str):  # Check if the value is a string
        if value.startswith("0x"):  # Handle hexadecimal strings
            return int(value, 16)
        else:  # Handle decimal strings
            return int(value)
    elif isinstance(value, int):  # Value is already an integer
        return value
    else:
        raise ValueError(f"Unsupported type for conversion: {type(value)}")
    
    
    
    





def preprocess(lines, filename="main.asm"):
    errors = []
    warnings = []
    error_flag = False

    # Memory and stack tracking
    instruction_count = 0
    memory_limit = 256  # Total memory available
    stack_balance = 0
    program_length = 0  # To calculate and validate memory access

    # Valid registers and instructions
    valid_registers = {"a", "b", "c", "d", "e", "f"}
    valid_instructions = {"ldw", "mov", "add", "sub", "str", "ldr", "int",
                          "push", "pop", "jsr", "ret", "xor", "and", "jmp",
                          "mul", "div", "bne", "beq", "blt"}
    label_references = []
    labels = {}

    # First pass: Parse instructions and calculate program length
    for line_number, line in enumerate(lines, start=1):
        code = line.split(";")[0].strip()  # Strip comments and whitespace
        if not code:
            continue

        # Handle labels
        if code.endswith(":"):
            label_name = code[:-1]
            if label_name in labels:
                warnings.append((line_number, f"duplicate label '{label_name}'", line))
            labels[label_name] = instruction_count
            continue

        # Parse instruction
        parts = re.split(r"\s+", code)
        instruction = parts[0].lower()
        if instruction in valid_instructions:
            if instruction in {"ldw", "mov", "add", "sub", "str", "ldr", "xor", "and", "mul", "div"}:
                instruction_count += 3  # These are 3-byte instructions
            elif instruction in {"bne", "beq", "blt"}:
                instruction_count += 4  # Conditional branches are 4-byte instructions
            elif instruction in {"push", "pop", "int", "jmp", "jsr", "ret"}:
                instruction_count += 3  # Fixed size for other instructions
        else:
            errors.append((line_number, f"unknown instruction '{instruction}'", line))
            error_flag = True

    program_length = instruction_count  # Final length of the program

    # Second pass: Validate instructions and operands
    for line_number, line in enumerate(lines, start=1):
        code = line.split(";")[0].strip()  # Strip comments and whitespace
        if not code:
            continue

        # Skip labels
        if code.endswith(":"):
            continue

        parts = re.split(r"\s+", code)
        instruction = parts[0].lower()
        operands = parts[1:] if len(parts) > 1 else []

        # Strip commas from registers and operands
        operands = [op.replace(",", "") for op in operands]

        # Validate instruction and operands
        if instruction == "ldw" and len(operands) == 2:
            reg, value = operands
            if reg not in valid_registers:
                errors.append((line_number, f"invalid register '{reg}'", line))
                error_flag = True
        elif instruction == "str" and len(operands) == 2:
            reg, address = operands
            if reg not in valid_registers:
                errors.append((line_number, f"invalid register '{reg}'", line))
                error_flag = True
            try:
                mem_address = int(address, 16)
                if mem_address < program_length:
                    errors.append((line_number, f"illegal memory write to program space in '{code}'", line))
                    error_flag = True
                if mem_address > memory_limit:
                    errors.append((line_number, f"illegal memory write out of bounds in '{code}'", line))
                    error_flag = True
                    
            except ValueError:
                errors.append((line_number, f"invalid memory address '{address}'", line))
                error_flag = True
        elif instruction in {"add", "sub", "mov", "xor", "and", "mul", "div"} and len(operands) == 2:
            reg1, reg2 = operands
            if reg1 not in valid_registers or reg2 not in valid_registers:
                errors.append((line_number, f"invalid register(s) in '{code}'", line))
                error_flag = True
        elif instruction in {"push", "pop"} and len(operands) == 1:
            reg = operands[0]
            if reg not in valid_registers:
                errors.append((line_number, f"invalid register '{reg}'", line))
                error_flag = True
            if instruction == "push":
                stack_balance += 1
                if stack_balance > 16:  # Example stack limit
                    warnings.append((line_number, "stack overflow detected", line))
            elif instruction == "pop":
                stack_balance -= 1
                if stack_balance < 0:
                    errors.append((line_number, f"stack underflow detected at '{code}'", line))
                    error_flag = True
        # Validate branch instructions with two registers and one label
        elif instruction in {"bne", "beq", "blt"}:
            if len(operands) != 3:
                errors.append((line_number, f"branch instruction '{instruction}' should have 2 registers and 1 label", line))
                error_flag = True
            else:
                reg1, reg2, label = operands
                if reg1 not in valid_registers or reg2 not in valid_registers:
                    errors.append((line_number, f"invalid register(s) in '{instruction}'", line))
                    error_flag = True
                label_references.append((line_number, label, line))  # The third operand should be a label
        
        elif instruction in {"jmp", "jsr"}:
            if len(operands) != 1:
                errors.append((line_number, f"'{instruction}' instruction should have 1 operand (label)", line))
                error_flag = True
            label = operands[0]  # The only operand should be a label
            label_references.append((line_number, label, line))

    # Check undefined labels
    for line_number, label, line in label_references:
        if label not in labels:
            errors.append((line_number, f"undefined label '{label}'", line))
            error_flag = True

    # Check stack balance at the end
    if stack_balance != 0:
        warnings.append((0, "stack imbalance detected, unbalanced push/pop operations", ""))

    # Print errors and warnings
    for line_number, message, code_line in errors:
        print(colored(f"{filename}:{line_number}: error: {message}", "red"))
        print(colored(f"   {line_number} | {code_line}", "white"))
        print(colored(f"      | {'^' * len(code_line)}", "cyan"))

    for line_number, message, code_line in warnings:
        if line_number == 0:
            print(colored(f"{filename}: warning: {message}", "yellow"))
        else:
            print(colored(f"{filename}:{line_number}: warning: {message}", "yellow"))
            print(colored(f"   {line_number} | {code_line}", "white"))
            
    if program_length >= memory_limit:
        error_flag = True
        print(colored(f"GLOBAL: error: Program too big, size: {program_length}", "red"))
        

    # Final success message
    if not error_flag:
        print(colored("Preprocessing complete. No errors detected!", "green"))
    else:
        exit(1)




preprocess(lines)


    






lineNumber = 0

def _ValueError(message):
    print("ValueError: %s on line:" % message, lineNumber)
    
def _IndexError(message):
    print("IndexError: %s on line:" % message, lineNumber)

def _InstructionError(message):
    print("InstructionError: %s on line:" % message, lineNumber)
    
    
    


# for line in lines:
#     line = line.split(";")[0] # filter out comments
#     print(line)
    
# Dictionary to store labels and associated instructions
label_to_instructions = {}
current_label = None




for line in lines:
    # Remove leading and trailing whitespace
    stripped_line = line.strip()
    
    if stripped_line.endswith(':'):
        # It's a label, use it as the new key in the dictionary
        current_label = stripped_line[:-1]  # Remove the colon
        current_label = current_label.upper()
        label_to_instructions[current_label] = []  # Initialize empty instruction list
    elif stripped_line:
        # It's an instruction; add it to the current label's list
        if current_label is not None:
            label_to_instructions[current_label].append(stripped_line)
            
            
            

# register letter to identifyer
registerDict = {'a':0x0,'b':0x1,'c':0x2,'d':0x3,'e':0x4,'f':0x5}



current_byte_offset = 0  # Tracks the current byte address
label_addresses = {}  # Maps label names to their resolved byte addresses

for label in label_to_instructions:
    label_addresses[label] = current_byte_offset
    for line in label_to_instructions[label]:
        line = line.strip().split(";")[0] # strip comments
        line = line.rstrip(" ") # strip spaces at end
        
        
        line = line.replace(",", "") # stupid way to remove commas but it works
        
        line = line.split(" ") # get each part of the instruction
        
        
        line[0] = line[0].lower() # make instruction lowercase
        
        if line[0] == '':
            continue
        
        if line[0] in {"ldw","mov","add","sub","str","ldr","int","push","pop","jsr", "ret", 'xor', 'and', 'jmp', 'mul', 'div'}: # 3 byte instructions
            current_byte_offset += 3
            
        elif line[0] in {'bne', 'beq', 'blt'}: # 4 byte instructions
            current_byte_offset += 4
    
    
    

current_byte_offset = 0  # Tracks the current byte address
#print(label_addresses)

outputBytes = []
for label in label_to_instructions:
    #print(label)
    if label_addresses[label] != current_byte_offset:
        raise IndexError(f"address mismatch, expected {label_addresses[label]}, got {current_byte_offset}")
    # Output the results
    for line in label_to_instructions[label]:
        line = line.strip().split(";")[0] # strip comments
        line = line.rstrip(" ") # strip spaces at end
        
        
        line = line.replace(",", "") # stupid way to remove commas but it works
        
        line = line.split(" ") # get each part of the instruction
        
        
        line[0] = line[0].lower() # make instruction lowercase
        
        if line[0] == '':
            continue
            
        #print(line)
        
        
        #! Code to convert to bytes
        bytes = []
        try:
            if line[0] == 'ldw': # Load immediate to register
                bytes.append(0x1) # byte for load immediate value
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
                bytes.append(convert_to_int(line[2])) # the actual value as an int
                
            elif line[0] == 'mov': # Load immediate to register
                bytes.append(0x2) # byte for load immediate value
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                #bytes.append(0x0)
                
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
                #bytes.append(convert_to_int(line[2])) # the actual value as an int
                
            elif line[0] == 'add': # Load immediate to register
                bytes.append(0x3) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
            elif line[0] == 'sub': # Load immediate to register
                bytes.append(0x4) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
            elif line[0] == 'str': # Load immediate to register
                bytes.append(0x5) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                
                bytes.append(convert_to_int(line[2])) # the actual value as an int
                    
            
            elif line[0] == 'ldr': # Load immediate to register
                bytes.append(0x6) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                
                bytes.append(convert_to_int(line[2])) # the actual value as an int
                    
                    
            elif line[0] == 'int': # Load immediate to register
                bytes.append(0xA) 
                
                bytes.append(convert_to_int(line[1])) # the actual value as an int
                
                bytes.append(0x0) #! NEED THIS TO KEEP THE INSTRUCTION AT 3 BYTES 
                
                
            elif line[0] == 'bne': # Load immediate to register
                bytes.append(0x8) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                
                label = line[3].upper()
                if label == -1:
                    _InstructionError("Missing Label")
                    continue
                
                if label in label_to_instructions:
                    bytes.append(label_addresses[label])
                else:
                    _InstructionError("Unknown Label")
                    
            elif line[0] == 'beq': # Load immediate to register
                bytes.append(0x9) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                
                label = line[3].upper()
                if label == -1:
                    _InstructionError("Missing Label")
                    continue
                
                if label in label_to_instructions:
                    bytes.append(label_addresses[label])
                else:
                    _InstructionError("Unknown Label")
                    
            elif line[0] == 'push': # Load immediate to register
                bytes.append(0xB) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                
                
                bytes.append(0x0) # padding
            elif line[0] == 'pop': # Load immediate to register
                bytes.append(0xC) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                
                bytes.append(0x0) # padding
                
            elif line[0] == 'jsr': # Load immediate to register
                bytes.append(0xD) 
                # set register ID:
                
                label = line[1].upper()
                if label == -1:
                    _InstructionError("Missing Label")
                    continue
                
                if label in label_to_instructions:
                    bytes.append(label_addresses[label])
                else:
                    _InstructionError("Unknown Label")
                
                bytes.append(0x0) # padding
                
            elif line[0] == 'ret': # Load immediate to register
                bytes.append(0xE) 
                # set register ID:
                bytes.append(0x0) # padding
                bytes.append(0x0) # padding
                
                    
            elif line[0] == 'xor': # Load immediate to register
                bytes.append(0xF) 
                
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
            elif line[0] == 'and': # Load immediate to register
                bytes.append(0x10) 
                
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
            elif line[0] == 'jmp': # Load immediate to register
                bytes.append(0x11) 
                # set register ID:
                
                label = line[1].upper()
                if label == -1:
                    _InstructionError("Missing Label")
                    continue
                
                if label in label_to_instructions:
                    bytes.append(label_addresses[label])
                else:
                    _InstructionError("Unknown Label")
                
                bytes.append(0x0) # padding
            
            
            
            elif line[0] == 'mul': # Load immediate to register
                bytes.append(0x12) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
            elif line[0] == 'div': # Load immediate to register
                bytes.append(0x13) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
            elif line[0] == 'blt': # Load immediate to register
                bytes.append(0x14) 
                # set register ID:
                register = registerDict.get(line[1].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                    
                register = registerDict.get(line[2].lower(),-1)
                if register >= 0 and register <= 5:
                    bytes.append(register)
                    
                else:
                    _ValueError("Invalid Register")
                
                
                label = line[3].upper()
                if label == -1:
                    _InstructionError("Missing Label")
                    continue
                
                if label in label_to_instructions:
                    bytes.append(label_addresses[label])
                else:
                    _InstructionError("Unknown Label")
                
                
            else:
                _InstructionError("Unknown Instruction")
                
                
                
        except IndexError:
            _IndexError("Maformed Instruction")
        except ValueError:
            _ValueError("Unknown Error")
            
        current_byte_offset += len(bytes)
        
            
        lineNumber+=1
        outputBytes += bytes
        

print(outputBytes)
            
        
    
    