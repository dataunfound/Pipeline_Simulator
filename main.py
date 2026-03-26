import os
import sys
import matplotlib.pyplot as plt

def load_instructions(file_path):
    """Reads raw assembly instructions from a text file."""
    instructions = []
    
    # Check file existence to ensure robust error handling
    if not os.path.exists(file_path):
        print(f"Error: Could not find '{file_path}'. Check the directory.")
        return None
        
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                # Ignore empty lines and comments
                if clean_line and not clean_line.startswith("#"): 
                    instructions.append(clean_line)
                    
        return instructions
    except Exception as e:
        print(f"File reading error: {e}")
        return None


def parse_instruction(instruction_string):
    """Parses a raw assembly string into a structured dictionary."""
    parts = instruction_string.replace(',', ' ').split()
    
    if not parts:
        return None
        
    opcode = parts[0].upper()
    
    parsed_data = {
        "raw_text": instruction_string,
        "opcode": opcode,
        "dest": None,   
        "src1": None,   
        "src2": None,   
        "imm": None     
    }
    
    try:
        if opcode in ["ADD", "SUB", "MUL", "DIV"]:
            parsed_data["dest"] = parts[1]
            parsed_data["src1"] = parts[2]
            parsed_data["src2"] = parts[3]
            
        elif opcode == "LOAD":
            parsed_data["dest"] = parts[1]
            mem_operand = parts[2]
            imm_str, reg_str = mem_operand.split('(')
            parsed_data["imm"] = int(imm_str)
            parsed_data["src1"] = reg_str.replace(')', '')
            
        elif opcode == "STORE":
            parsed_data["src2"] = parts[1] 
            mem_operand = parts[2]
            imm_str, reg_str = mem_operand.split('(')
            parsed_data["imm"] = int(imm_str)
            parsed_data["src1"] = reg_str.replace(')', '')
        else:
            return None
            
    except (IndexError, ValueError):
        return None
        
    return parsed_data


class PipelineSimulator:
    def __init__(self, instructions):
        self.instructions = instructions
        self.pc = 0
        self.clock_cycle = 0
        self.total_stalls = 0
        
        self.stages = {
            "IF": None,
            "ID": None,
            "EX": None,
            "MEM": None,
            "WB": None
        }
        self.is_done = False

    def detect_data_hazard(self):
        """
        Searches active pipeline stages to detect RAW data hazards.
        Implements 'Internal Forwarding' hardware optimization.
        """
        id_inst = self.stages["ID"]
        
        if not id_inst or id_inst["opcode"] == "STALL":
            return False

        src_regs = [id_inst["src1"], id_inst["src2"]]
        src_regs = [reg for reg in src_regs if reg is not None]

        if not src_regs:
            return False

        # EX and MEM are searched. WB is excluded to simulate internal hardware forwarding,
        # allowing ID to read the value in the exact cycle it is written by WB.
        for stage in ["EX", "MEM"]:
            active_inst = self.stages[stage]
            if active_inst and active_inst["opcode"] != "STALL" and active_inst["dest"] is not None:
                if active_inst["dest"] in src_regs:
                    return True 

        return False

    def step(self):
        """Simulates one clock cycle of the CPU."""
        self.clock_cycle += 1
        
        stall_pipeline = self.detect_data_hazard()

        if stall_pipeline:
            self.total_stalls += 1
            self.stages["WB"] = self.stages["MEM"]
            self.stages["MEM"] = self.stages["EX"]
            # Insert STALL bubble into EX
            self.stages["EX"] = {
                "opcode": "STALL", "dest": None, "src1": None, "src2": None, "imm": None
            }
        else:
            self.stages["WB"] = self.stages["MEM"]
            self.stages["MEM"] = self.stages["EX"]
            self.stages["EX"] = self.stages["ID"]
            self.stages["ID"] = self.stages["IF"]
            
            if self.pc < len(self.instructions):
                self.stages["IF"] = self.instructions[self.pc]
                self.pc += 1
            else:
                self.stages["IF"] = None
                
        active_instructions = [
            inst for inst in self.stages.values() 
            if inst is not None and inst["opcode"] != "STALL"
        ]
        if not active_instructions and self.pc >= len(self.instructions):
            self.is_done = True

    def print_state(self):
        """Prints the current pipeline state to the terminal."""
        print(f"\n[Clock Cycle: {self.clock_cycle}]")
        for stage, inst in self.stages.items():
            inst_name = inst["opcode"] if inst else "Empty"
            if inst_name == "STALL":
                print(f"  {stage:<3} : * {inst_name} *")
            else:
                print(f"  {stage:<3} : {inst_name}")

    def plot_performance(self):
        """
        Generates a graphical bar chart comparing ideal execution time 
        versus actual execution time delayed by hazards.
        """
        # A perfect 5 stage pipeline takes (N + 4) cycles to complete N instructions
        ideal_cycles = len(self.instructions) + 4
        actual_cycles = self.clock_cycle

        labels = ['Ideal (No Hazards)', 'Actual (With Hazards)']
        values = [ideal_cycles, actual_cycles]
        colors = ['#4CAF50', '#F44336'] # Green for ideal, Red for actual

        plt.figure(figsize=(8, 5))
        bars = plt.bar(labels, values, color=colors)
        
        plt.title('CPU Pipeline Performance Analysis')
        plt.ylabel('Total Clock Cycles')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Add numerical labels on top of the bars for clarity
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', fontweight='bold')

        print("\nOpening performance graph window...")
        plt.show()


def main():
    print("Pipeline Hazard Simulator\n")
    
    file_name = "instructions.txt"
    raw_instructions = load_instructions(file_name)
    if not raw_instructions:
        sys.exit(1)
        
    parsed_program = []
    for line in raw_instructions:
        parsed_inst = parse_instruction(line)
        if parsed_inst:
            parsed_program.append(parsed_inst)
            
    print(f"Loaded and parsed {len(parsed_program)} instructions.\n")
    print("Starting Pipeline Simulation...")
    
    simulator = PipelineSimulator(parsed_program)
    
    while not simulator.is_done:
        simulator.step()
        simulator.print_state()
        
    print(f"\nSimulation finished in {simulator.clock_cycle} clock cycles.")
    print(f"Total Stalls (Hazards Prevented): {simulator.total_stalls}")
    
    # Trigger the data visualization
    simulator.plot_performance()

if __name__ == "__main__":
    main()