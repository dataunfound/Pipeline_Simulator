import os
import sys

def load_instructions(file_path):
    """Reads raw assembly instructions from a text file."""
    instructions = []
    
    # I check for the file's existence first to ensure the simulator is robust.
    # This prevents the program from crashing if the input file is missing.
    if not os.path.exists(file_path):
        print(f"Error: Could not find '{file_path}'. Check the directory.")
        return None
        
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                # Skipping empty lines and manual comments (starting with #) 
                # helps the parser focus only on executable code.
                if clean_line and not clean_line.startswith("#"): 
                    instructions.append(clean_line)
                    
        print(f"Successfully loaded {len(instructions)} instructions.")
        return instructions
        
    except Exception as e:
        # Standard safety net for any unexpected I/O issues.
        print(f"File reading error: {e}")
        return None


def parse_instruction(instruction_string):
    """
    Parses a raw assembly string into a structured dictionary.
    This fulfills the 'complex data structures' requirement.
    """
    # Replacing commas with spaces makes it easier to split the instruction parts.
    parts = instruction_string.replace(',', ' ').split()
    
    if not parts:
        return None
        
    opcode = parts[0].upper()
    
    # I used a dictionary structure to store opcode and registers separately.
    # This is essential for detecting data hazards in later stages.
    parsed_data = {
        "raw_text": instruction_string,
        "opcode": opcode,
        "dest": None,   # Write register
        "src1": None,   # Read register 1
        "src2": None,   # Read register 2
        "imm": None     # Memory offset
    }
    
    try:
        # Arithmetic logic (ADD R1, R2, R3)
        if opcode in ["ADD", "SUB", "MUL", "DIV"]:
            parsed_data["dest"] = parts[1]
            parsed_data["src1"] = parts[2]
            parsed_data["src2"] = parts[3]
            
        # I handle LOAD and STORE differently because their register usage is opposite.
        elif opcode == "LOAD":
            # LOAD R6, 100(R2) -> R6 is where the data is written (Destination).
            parsed_data["dest"] = parts[1]
            mem_operand = parts[2]
            imm_str, reg_str = mem_operand.split('(')
            parsed_data["imm"] = int(imm_str)
            parsed_data["src1"] = reg_str.replace(')', '')
            
        elif opcode == "STORE":
            # STORE R6, 200(R4) -> R6 is the data being read to be saved (Source).
            # It doesn't change the register, so dest stays None.
            parsed_data["src2"] = parts[1] 
            mem_operand = parts[2]
            imm_str, reg_str = mem_operand.split('(')
            parsed_data["imm"] = int(imm_str)
            parsed_data["src1"] = reg_str.replace(')', '')
            
        else:
            print(f"Warning: Unknown instruction '{opcode}'. Skipping.")
            return None
            
    except (IndexError, ValueError):
        # This catch-all ensures the program doesn't break if an instruction has a typo.
        print(f"Error: Malformed syntax -> '{instruction_string}'. Skipping.")
        return None
        
    return parsed_data


def main():
    print("Pipeline Hazard Simulator")
    print("-" * 25)
    
    # Step 1: Loading
    file_name = "instructions.txt"
    raw_instructions = load_instructions(file_name)
    
    if not raw_instructions:
        print("\nExiting: Missing or unreadable input file.")
        sys.exit(1)
        
    # Step 2: Parsing
    print("\nParsing instructions...")
    parsed_program = []
    
    for line in raw_instructions:
        parsed_inst = parse_instruction(line)
        if parsed_inst:
            parsed_program.append(parsed_inst)
            
    print(f"Parsed {len(parsed_program)} instructions successfully.")
    
    # Step 3: Verifying (Debug View)
    if parsed_program:
        print("\nStructured Program Memory:")
        for idx, inst in enumerate(parsed_program):
            print(f"  [{idx}] Opcode: {inst['opcode']:<5} | Dest: {str(inst['dest']):<4} | Src1: {str(inst['src1']):<4} | Src2: {str(inst['src2']):<4} | Imm: {str(inst['imm'])}")

if __name__ == "__main__":
    main()