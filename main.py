import os
import sys

def load_instructions(file_path):
    instructions = []
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find '{file_path}'. Please ensure the file is in the correct directory.")
        return None
        
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith("#"): 
                    instructions.append(clean_line)
                    
        print(f"Successfully loaded {len(instructions)} instructions.")
        return instructions
        
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def main():
    print("Pipeline Hazard Simulator")
    print("-" * 25)
    
    file_name = "instructions.txt"
    instruction_memory = load_instructions(file_name)
    
    if instruction_memory:
        print("\nCurrent Instruction Memory:")
        for idx, inst in enumerate(instruction_memory):
            print(f"  [{idx}] {inst}")
    else:
        print("\nExiting simulator due to missing or unreadable input file.")
        sys.exit(1)

if __name__ == "__main__":
    main()