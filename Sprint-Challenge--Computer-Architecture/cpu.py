import sys


# Instructions
HLT = 0b00000001  # Exit opcode
LDI = 0b10000010  # Set op_a register to value op_b
PRN = 0b01000111  # Print
MUL = 0b10100010  # ALU opcode
PUSH = 0b01000101 # Stack opcode
POP = 0b01000110  # Stack opcode

# SPRINT CHALLENGE
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0  # Program counter
        self.ram = [0] * 256
        self.reg = [0] * 8  # Only vals b/t 0-255, bitwise AND results with 0xFF
        self.reg[7] = 0xf4  # Reserved register: Stack pointer, grows down
        self.sp = self.reg[7]
        # Flag value set by CMP: 0b00000LGE
        self.fl = 0b00000000

        self.dispatch_table = {}
        self.dispatch_table[HLT] = self.handle_HLT
        self.dispatch_table[LDI] = self.handle_LDI
        self.dispatch_table[PRN] = self.handle_PRN
        self.dispatch_table[MUL] = self.handle_MUL
        self.dispatch_table[PUSH] = self.handle_PUSH
        self.dispatch_table[POP] = self.handle_POP

        # SPRINT CHALLENGE
        self.dispatch_table[CMP] = self.handle_CMP
        self.dispatch_table[JMP] = self.handle_JMP
        self.dispatch_table[JEQ] = self.handle_JEQ
        self.dispatch_table[JNE] = self.handle_JNE

    def handle_HLT(self):
        sys.exit(0)  # Successful exit

    def handle_PRN(self):
        op_a = self.ram_read(self.pc+1)
        print(self.ram[op_a])

    def handle_MUL(self):
        # Read values to multiply
        op_a = int(self.ram_read(self.pc+1))  # RAM Register a
        op_b = int(self.ram_read(self.pc+2))  # RAM Register b
        # Copy values to ALU register
        self.reg[op_a] = self.ram_read(op_a)
        self.reg[op_b] = self.ram_read(op_b)
        # Perform ALU computation, overwrite RAM register op_a
        self.ram_write(op_a, self.alu("MUL", op_a, op_b))

    def handle_LDI(self):
        op_a = int(self.ram_read(self.pc+2))  # Value in base10
        op_b = int(self.ram_read(self.pc+1))  # Register in base10
        self.ram_write(op_b, op_a)

    def handle_PUSH(self):
        # Decrement stack pointer
        self.sp -= 1
        # Copy value in register to SP address
        op_a = self.ram_read(self.ram_read(self.pc+1))
        self.ram_write(self.sp, op_a)

    def handle_POP(self):
        # Copy val from self.sp address to register
        op_a = self.ram_read(self.pc+1)
        self.ram_write(op_a, self.ram_read(self.sp))
        # Increment stack pointer
        self.sp += 1

    def handle_CMP(self):
        # Read values to compare
        op_a = int(self.ram_read(self.pc+1))  # RAM Register a
        op_b = int(self.ram_read(self.pc+2))  # RAM Register b
        # Copy values to ALU register
        self.reg[op_a] = self.ram_read(op_a)
        self.reg[op_b] = self.ram_read(op_b)
        # Perform ALU computation: compare and set flag
        self.alu("CMP", op_a, op_b)

    def handle_JMP(self):
        # Set PC to address stored in given register
        op_a = int(self.ram_read(self.pc+1))  # Register storing jump addr
        self.pc = self.ram_read(op_a)

    def handle_JEQ(self):
        # Jump if Equality FLAG is True
        op_a = int(self.ram_read(self.pc+1))  # Register storing jump addr
        if self.fl == 0b00000001:
            self.pc = self.ram_read(op_a)

    def handle_JNE(self):
        # Jump if Equality FLAG is False/0
        op_a = int(self.ram_read(self.pc+1))  # Register storing jump addr
        if self.fl == 0b00000100:
            self.pc = self.ram_read(op_a)
        elif self.fl == 0b00000010:
            self.pc = self.ram_read(op_a)

    def load(self):
        """Load a program into memory."""
        program = []
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            for line in f:
                if line[:8].isnumeric():
                    command = int(line[:8], 2)
                    program.append(command)
        f.close()

        address = 0
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
        return

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            return self.reg[reg_a]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            return self.reg[reg_a]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            else:
                self.fl = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            # Instruction register
            IR = self.ram[self.pc]

            # Calculate PC increment value: get high bits 6 & 7
            operand_count = IR >> 6
            instr_len = operand_count + 1

            # Dispatch table
            pre_exec_pc = self.pc
            self.dispatch_table[IR]()
            post_exec_pc = self.pc

            # Increment PC normally if IR doesn't set the PC
            if IR == JMP:
                # Unconditionally don't increment PC
                continue
            elif (IR == JEQ) or (IR == JNE):
                # If PC didn't jump during opcode execution
                if post_exec_pc == pre_exec_pc:
                    self.pc += instr_len
                else:
                    continue
            else:
                self.pc += instr_len
