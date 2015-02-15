# Implementation of FIR filter in Arm Thumb assembler
# Author: Peter Hinch
# 15th Feb 2015
# Updated to reflect support for push and pop
# Calculate coefficients here: http://t-filter.appspot.com/fir/index.html

# Function arguments:
# r1 is an integer array of coefficients
# r0 is an integer scratchpad array. Must be of length 3 greater than the # of coefficients.
# Entry:
# array[0] must hold the array length
# array[1] the number of bits to scale (right shift) the result (0-31).
# other elements must be zero

# Run conditions
# array[2] holds the insertion point address
# r2 holds the new data value
# Register usage (Buffer)
# r0 Scratchpad
# r2 new data value
# r3 ring buffer start
# r4 insertion point (post increment)
# r5 last location in ring buffer

# Register usage (filter)
# r0 accumulator for result
# r1 coefficient array
# r2 current coeff
# r3 ring buffer start
# r4 insertion point (post increment)
# r5 last location in ring buffer
# r6 data point counter
# r7 curent data value
# r8 scaling value

@micropython.asm_thumb
def fir(r0, r1, r2):
    push({r8})
    ldr(r7, [r0, 0])    # Array length
    mov(r6, r7)         # Copy for filter
    mov(r3, r0)
    add(r3, 12)         # r3 points to ring buffer start
    sub(r7, 1)
    add(r7, r7, r7)
    add(r7, r7, r7)     # convert to bytes
    add(r5, r7, r3)     # r5 points to ring buffer end (last valid address)
    ldr(r4, [r0, 8])    # Current insertion point address
    cmp(r4, 0)          # If it's zero we need to initialise
    bne(INITIALISED)
    mov(r4, r3)         # Initialise: point to buffer start
    label(INITIALISED)
    str(r2, [r4, 0])    # put new data in buffer and post increment
    add(r4, 4)
    cmp(r4, r5)         # Check for buffer end
    ble(BUFOK)
    mov(r4, r3)         # Incremented past end: point to start
    label(BUFOK)
    str(r4, [r0, 8])    # Save the insertion point for next call
                        # *** Filter ***
    ldr(r0, [r0, 4])    # Bits to shift ??????????
    mov(r8, r0)
    mov(r0, 0)          # r0 Accumulator
    label(FILT)
    ldr(r7, [r4, 0])    # r7 Data point (start with oldest)
    add(r4, 4)
    cmp(r4, r5)
    ble(NOLOOP1)
    mov(r4, r3)
    label(NOLOOP1)
    ldr(r2, [r1, 0])    # r2 Coefficient
    add(r1, 4)          # Point to next coeff
    mul(r2, r7)
    mov(r7, r8)
    asr(r2, r7)         # Scale result before summing
    add(r0, r2, r0)
    sub(r6, 1)
    bpl(FILT)
    pop({r8})

