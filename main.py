import os
import sys

def load_instructions(file_path):
    """Reads raw assembly instructions from a text file."""
    instructions = []
    
    # Checking if the file exists before opening it prevents the whole simulator from crashing.
    # This makes the program robust against missing files or bad inputs.
    if not os.path.exists(file_path):
        print(f"Error: Could not find '{file_path}'. Check the directory.")
        return None
        
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                # Ignoring empty lines and comments starting with '#'
                # so the pipeline only processes actual executable commands.
                if clean_line and not clean_line.startswith("#"): 
                    instructions.append(clean_line)
                    
        print(f"Successfully loaded {len(instructions)} instructions.")
        return instructions
        
    except Exception as e:
        # Catching generic exceptions as a safety net for unexpected file reading issues.
        print(f"File reading error: {e}")
        return None


def parse_instruction(instruction_string):
    """
    Parses a raw assembly instruction string into a structured dictionary.
    """
    # Replacing commas with spaces creates a uniform format before splitting the string.
    # This simplifies the parsing logic and reduces formatting errors.
    parts = instruction_string.replace(',', ' ').split()
    
    if not parts:
        return None
        
    opcode = parts[0].upper()
    
    # Using a dictionary for the complex data structures requirement.
    # Structuring the data this way makes it much easier to detect data hazards in the pipeline stages.
    parsed_data = {
        "raw_text": instruction_string,
        "opcode": opcode,
        "dest": None,   
        "src1": None,   
        "src2": None,   
        "imm": None     
    }
    
    try:
        # Arithmetic operations (ADD R1, R2, R3)
        if opcode in ["ADD", "SUB", "MUL", "DIV"]:
            parsed_data["dest"] = parts[1]
            parsed_data["src1"] = parts[2]
            parsed_data["src2"] = parts[3]
            
        # Memory access operations (LOAD R6, 100(R2))
        elif opcode in ["LOAD", "STORE"]:
            parsed_data["dest"] = parts[1]
            
            mem_operand = parts[2]
            imm_str, reg_str = mem_operand.split('(')
            
            parsed_data["imm"] = int(imm_str)
            parsed_data["src1"] = reg_str.replace(')', '')
            
        else:
            print(f"Warning: Unknown instruction '{opcode}'. Skipping.")
            return None
            
    except (IndexError, ValueError):
        # If an instruction has missing parts (ADD R1), this block catches it.
        # Keeps the program running smoothly even with bad inputs.
        print(f"Error: Malformed syntax -> '{instruction_string}'. Skipping.")
        return None
        
    return parsed_data


def main():
    print("Pipeline Hazard Simulator")
    print("-" * 25)
    
    file_name = "instructions.txt"
    raw_instructions = load_instructions(file_name)
    
    if not raw_instructions:
        print("\nExiting simulator: missing or unreadable input file.")
        sys.exit(1)
        
    print("\nParsing instructions...")
    parsed_program = []
    
    for line in raw_instructions:
        parsed_inst = parse_instruction(line)
        if parsed_inst:
            parsed_program.append(parsed_inst)
            
    print(f"Parsed {len(parsed_program)} instructions.")
    
    if parsed_program:
        print("\nStructured Program Memory:")
        for idx, inst in enumerate(parsed_program):
            print(f"  [{idx}] Opcode: {inst['opcode']:<5} | Dest: {str(inst['dest']):<3} | Src1: {str(inst['src1']):<3} | Src2: {str(inst['src2']):<3} | Imm: {str(inst['imm'])}")

if __name__ == "__main__":
    main()