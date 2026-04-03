# Pipeline Hazard Simulator

**Course:** IY499 Independent Project

**Difficulty Level:** Advanced

## Project Overview
This project is an object-oriented Python simulator for a five-stage CPU pipeline. The main goal is to show how a processor executes assembly instructions in each clock cycle. It specifically focuses on detecting and handling read-after-write data hazards by using pipeline stalling and internal forwarding logic.

I chose this project to connect theoretical computer architecture with practical software engineering. Building this simulator helped me demonstrate complex data structuring, algorithmic search implementations, and solid error handling in Python.

## Key Features
* **Instruction Parsing:** Converts raw text into structured dictionaries to keep track of registers easily.
* **File Input Safety:** Includes strict try-except error checking to stop the program from crashing if a file is missing or if the instruction syntax is wrong.
* **Pipeline Engine:** Simulates the five standard stages (Instruction Fetch, Instruction Decode, Execute, Memory Access, and Writeback) in exact chronological order.
* **Smart Hazard Detection:** Actively scans the active stages to find data dependencies. When a hazard is found, it injects a STALL bubble and dynamically reports exactly which register caused the delay (e.g., `STALL (Wait R1)`).
* **Hardware Optimization:** Implements internal forwarding. This allows the decode stage to read a register in the exact same cycle it gets updated, which significantly reduces unnecessary stalls.
* **Rich UX & Data Visualization:** Features a color-coded terminal interface for clear cycle tracking, and uses the `matplotlib` library to show a final bar chart comparing ideal performance with the actual clock cycles taken.

## Prerequisites
You need Python 3 installed on your system. The project also requires the `matplotlib` library to draw the performance charts.

You can install the required library by typing this in your terminal:
`pip install matplotlib`

## How to Run
1. Make sure your assembly instructions are saved in a file named `instructions.txt` in the exact same folder as the script.
2. Open your command line or terminal.
3. Run the script:
   `python main.py`
4. The terminal will print the simulation step by step with color coding. When it finishes, a window will automatically open to show the performance analysis chart.

## Input Format (instructions.txt)
The simulator reads standard assembly instructions. Right now it supports basic arithmetic and memory access commands. It safely ignores empty lines and comments that start with a `#` symbol.

**Example Input:**
```text
# Basic dependency test
ADD R1, R2, R3
SUB R4, R1, R5
LOAD R6, 100(R2)
STORE R6, 200(R4)
