# Examples of the workround for unimplemented assembler instructions
# Author: Peter Hinch
# 12th Feb 2015

# Source: ARM v7-M Architecture Reference Manual

# Make r8-r11 safe to use by pushing them on the stack
@micropython.asm_thumb
def foo(r0):
    data(2, 0xe92d, 0x0f00) # push r8,r9,r10,r11
    mov(r8, r0)             # Would otherwise crash the board!
    data(2, 0xe8bd, 0x0f00) # pop r8,r9,r10,r11

# The signed divide instruction
@micropython.asm_thumb
def div(r0, r1):
    data(2, 0xfb90, 0xf0f1)

# Bit reversal
@micropython.asm_thumb
def rbit(r0):
    data(2, 0xfa90, 0xf0a0)

# Count leading zeros
@micropython.asm_thumb
def clz(r0):
    data(2, 0xfab0, 0xf080)

# Count trailing zeros
@micropython.asm_thumb
def clz(r0):
    data(2, 0xfa90, 0xf0a0) # Bit reverse
    data(2, 0xfab0, 0xf080) # count leading zeros

@micropython.asm_thumb
def clz(r0):
    cmp(r0, r0)
    ite.ge
    add(r0, r0, r1)
    sub(r0, r0, r1)

