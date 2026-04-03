# Pipeline Hazard Simulator

**Course:** IY499 Independent Project
**Difficulty Level:** Advanced

## Project Overview
This project is a terminal-based, 5-stage CPU Pipeline Simulator built with Python. Its primary purpose is to simulate how a processor executes assembly instructions cycle-by-cycle and, more importantly, how it detects and handles Read-After-Write (RAW) data hazards using pipeline stalling and internal forwarding logic.

I chose this project to bridge the gap between theoretical computer architecture and practical software engineering. By building this simulator, I aimed to demonstrate complex data structuring, algorithmic search implementations, and robust error handling.

## Key Features
* **Instruction Parsing:** Converts raw text strings into structured dictionaries for precise register tracking.
* **Robust File I/O:** Includes comprehensive error checking to prevent crashes from missing files or malformed instruction syntax.
* **5-Stage Pipeline Engine:** Simulates the Fetch (IF), Decode (ID), Execute (EX), Memory (MEM), and Write-back (WB) stages in strict chronological order.
* **Hazard Detection Algorithm:** Actively scans the pipeline to detect data dependencies between adjacent instructions (RAW hazards) and injects 'STALL' bubbles to prevent data corruption.
* **Hardware Optimization:** Implements "Internal Forwarding" by allowing the Decode stage to read a register in the same cycle the Write-back stage updates it, reducing unnecessary stalls.
* **Data Visualization:** Uses `matplotlib` to generate a comparative bar chart showing ideal vs. actual clock cycles.

## Prerequisites
To run this simulator, you need Python 3 installed on your system, along with the `matplotlib` library for data visualization.

You can install the required library using:
`pip install matplotlib`

## How to Run
1. Ensure your assembly instructions are saved in a file named `instructions.txt` in the same directory as the script.
2. Open your terminal or command prompt.
3. Run the main script:
   `python main.py`
4. The terminal will output the cycle-by-cycle simulation. Once finished, a window will pop up displaying the performance analysis chart.

## Input Format (`instructions.txt`)
The simulator accepts standard assembly instructions. It currently supports basic Arithmetic and Memory Access commands. Empty lines and comments (starting with `#`) are safely ignored.

**Example Input:**
# Basic dependency test
ADD R1, R2, R3
SUB R4, R1, R5
LOAD R6, 100(R2)
STORE R6, 200(R4)

## Assessment Criteria Met
* **Complex Data Structures:** Used lists of nested dictionaries to maintain the state of the pipeline and parsed instructions.
* **Algorithms:** Developed a custom searching algorithm to look ahead in the pipeline stages for matching destination/source registers.
* **Error Handling:** Implemented `try-except` blocks to handle malformed strings and missing files gracefully without crashing the main loop.
* **Code Quality:** Used Object-Oriented Programming (OOP) principles by encapsulating the simulator state within a class.
