import os
import sys
import matplotlib.pyplot as plt

# Added ANSI color codes to make the terminal output easier to read, 
# especially for spotting STALL states visually.
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def load_instructions(file_path):
    # Checking if the file exists first to prevent unexpected crashes.
    instructions = []
    if not os.path.exists(file_path):
        print(f"{Colors.RED}Error: Could not find '{file_path}'. Check the directory.{Colors.RESET}")
        return None
        
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith("#"): 
                    instructions.append(clean_line)
        return instructions
    except Exception as e:
        print(f"{Colors.RED}File reading error: {e}{Colors.RESET}")
        return None

def parse_instruction(instruction_string):
    # Converting the entire string to UPPERCASE to handle case-insensitivity seamlessly.
    # Separating the destination and source registers makes hazard detection easier.
    parts = instruction_string.upper().replace(',', ' ').split()
    if not parts: return None
        
    opcode = parts[0]
    parsed_data = {
        "raw_text": instruction_string,
        "opcode": opcode,
        "dest": None, "src1": None, "src2": None, "imm": None     
    }
    
    # Using a try-except block here as a safety net. 
    # Catching IndexError gracefully if a line is missing operands.
    try:
        if opcode in ["ADD", "SUB", "MUL", "DIV"]:
            parsed_data["dest"] = parts[1]
            parsed_data["src1"] = parts[2]
            parsed_data["src2"] = parts[3]
        elif opcode == "LOAD":
            parsed_data["dest"] = parts[1]
            imm_str, reg_str = parts[2].split('(')
            parsed_data["imm"] = int(imm_str)
            parsed_data["src1"] = reg_str.replace(')', '')
        elif opcode == "STORE":
            parsed_data["src2"] = parts[1] 
            imm_str, reg_str = parts[2].split('(')
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
        
        # Representing the 5 pipeline stages. None implies the stage is currently empty (a bubble).
        self.stages = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}
        self.is_done = False

    def detect_data_hazard(self):
        # Core logic for detecting RAW (Read-After-Write) hazards. 
        # Checks if ID stage needs a register currently being modified by EX or MEM.
        id_inst = self.stages["ID"]
        if not id_inst or "STALL" in id_inst["opcode"]:
            return False, None

        src_regs = [id_inst["src1"], id_inst["src2"]]
        src_regs = [reg for reg in src_regs if reg is not None]

        if not src_regs:
            return False, None

        # Simulated 'Internal Forwarding' hardware optimization. 
        # WB stage is excluded so data can be read in the same cycle it is written.
        for stage in ["EX", "MEM"]:
            active_inst = self.stages[stage]
            if active_inst and "STALL" not in active_inst["opcode"] and active_inst["dest"] is not None:
                if active_inst["dest"] in src_regs:
                    return True, active_inst["dest"] 

        return False, None

    def step(self):
        self.clock_cycle += 1
        has_hazard, blocking_reg = self.detect_data_hazard()

        # Shifting instructions right-to-left (WB down to IF) to ensure data isn't overwritten.
        if has_hazard:
            self.total_stalls += 1
            self.stages["WB"] = self.stages["MEM"]
            self.stages["MEM"] = self.stages["EX"]
            # If hazard is found, freeze IF and ID, inject smart STALL bubble into EX.
            self.stages["EX"] = {
                "opcode": f"STALL (Wait {blocking_reg})", "dest": None, "src1": None, "src2": None, "imm": None
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
            if inst is not None and "STALL" not in inst["opcode"]
        ]
        if not active_instructions and self.pc >= len(self.instructions):
            self.is_done = True

    def print_state(self):
        print(f"\n{Colors.BLUE}{Colors.BOLD}[Clock Cycle: {self.clock_cycle}]{Colors.RESET}")
        for stage, inst in self.stages.items():
            inst_name = inst["opcode"] if inst else "Empty"
            if "STALL" in inst_name:
                print(f"  {Colors.YELLOW}{stage:<3}{Colors.RESET} : {Colors.RED}* {inst_name} *{Colors.RESET}")
            elif inst_name == "Empty":
                print(f"  {Colors.YELLOW}{stage:<3}{Colors.RESET} : {inst_name}")
            else:
                print(f"  {Colors.YELLOW}{stage:<3}{Colors.RESET} : {Colors.GREEN}{inst_name}{Colors.RESET}")

    def plot_performance(self):
        # Generates a polished bar chart visually comparing ideal vs actual performance.
        ideal_cycles = len(self.instructions) + 4
        
        # Subtracted 1 to account for the final pipeline flush cycle
        actual_cycles = self.clock_cycle - 1 

        labels = ['Ideal (No Hazards)', 'Actual (With Hazards)']
        values = [ideal_cycles, actual_cycles]
        bar_colors = ['#4CAF50', '#F44336'] 

        plt.figure(figsize=(8, 5))
        
        # Added edge colors to make the bars look sharper
        bars = plt.bar(labels, values, color=bar_colors, edgecolor='#333333', linewidth=1.2)
        
        plt.title('CPU Pipeline Performance Analysis', fontsize=14, fontweight='bold', pad=15)
        plt.ylabel('Total Clock Cycles', fontsize=12, labelpad=10)
        
        # DYNAMIC Y-AXIS LIMIT: Adds 20% headroom to the top so numbers don't hit the frame
        max_y = max(values)
        plt.ylim(0, max_y * 1.2)
        
        # Puts grid behind the bars
        plt.grid(axis='y', linestyle='--', alpha=0.6, zorder=0)

        for bar in bars:
            yval = bar.get_height()
            # Moved text slightly higher (va='bottom') for better spacing
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.3, int(yval), 
                     ha='center', va='bottom', fontweight='bold', fontsize=12)

        # UI Fix: Removing top and right borders for a cleaner, modern look
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Ensures everything fits beautifully without getting cut off
        plt.tight_layout()

        print(f"\n{Colors.HEADER}Opening performance graph window...{Colors.RESET}")
        plt.show()

def main():
    print(f"{Colors.BOLD}Pipeline Hazard Simulator{Colors.RESET}\n")
    
    file_name = "instructions.txt"
    raw_instructions = load_instructions(file_name)
    if not raw_instructions:
        sys.exit(1)
        
    parsed_program = []
    for line in raw_instructions:
        parsed_inst = parse_instruction(line)
        if parsed_inst:
            parsed_program.append(parsed_inst)
            
    print(f"{Colors.GREEN}Loaded and parsed {len(parsed_program)} instructions.{Colors.RESET}\n")
    
    # Safety lock against empty or entirely commented files.
    if len(parsed_program) == 0:
        print(f"{Colors.RED}No valid executable instructions found. Exiting...{Colors.RESET}")
        sys.exit(1)
        
    print("Starting Pipeline Simulation...")
    
    simulator = PipelineSimulator(parsed_program)
    
    # The main simulation loop. Keeps ticking the clock until all stages are completely empty.
    while not simulator.is_done:
        simulator.step()
        simulator.print_state()
        
    # Subtracted 1 from clock_cycle to account for the final flush cycle correctly
    print(f"\n{Colors.BOLD}Simulation finished in {simulator.clock_cycle - 1} clock cycles.{Colors.RESET}")
    print(f"{Colors.BOLD}Total Stalls (Hazards Prevented): {simulator.total_stalls}{Colors.RESET}")
    
    simulator.plot_performance()

if __name__ == "__main__":
    main()