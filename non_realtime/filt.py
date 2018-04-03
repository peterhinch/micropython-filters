# filt.py Perform FIR filtering (discrete convolution) on a 16-bit integer
# array of samples.
# Author: Peter Hinch
# 25th March 2018

# The MIT License (MIT)
#
# Copyright (c) 2018 Peter Hinch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Register usage
# r0, r1, r2 are used as variable pointers into their arrays.
# r0 sample set, halfword array for dcf, float for dcf_fp
# r1 result array, float, same length as sample set. Initially r[0] is scaling factor (default 1)
# r2 coeffs, float.
# r3 setup, int array [iplen, coeff_len, flags, decimate, offset] If decimate == 0 don't copy back to I/P
# After initial setup r3 is scratch.
# r4 scratch
# r5 coeff counter
# r6 cidx: index into samples as coeffs are processed.
# r7 addr of sample set start
# r8 no. of samples
# r9 addr of coeffs
# r10 Point to one sample after end of sample set
# r11 Flags
# r12 No. of coeffs
# s0 scaling factor
# s1 mean
# s2 current sample
# s3 res
# s4 current coeff
# s5 0.0
# s6 Coeff inc/dec amount (+4 or -4)
# s7 No. of samples to process (decrements)
# s8 Start of result array
# s9 Bytes to decrement sample pointer
# s10 No. of samples to process (constant)
# Flag bits. 
WRAP = const(1)
SCALE = const(2)
REVERSE = const(4)
COPY = const(8)

@micropython.asm_thumb
def dcf(r0, r1, r2, r3):
    push({r8, r9, r10, r11, r12})
    # Populate registers
    vmov(s8, r1)
    ldr(r4, [r3, 8])
    mov(r11, r4)  # R11 = Flags
    mov(r7, SCALE)
    tst(r4, r7)
    ittte(eq)
    mov(r5, 1)  # No scale factor: s0 = 1.0
    vmov(s0, r5)
    vcvt_f32_s32(s0, s0)
    vldr(s0, [r1, 0])  # S0 = scaling factor from op array

    mov(r4, 0)
    vmov(s5, r4)
    vcvt_f32_s32(s5, s5)  # S5 = 0.0

    mov(r7, r0)  # R7 -> sample set start
    mov(r9, r2)  # R9 -> coeff start

    ldr(r4, [r3, 0])
    mov(r8, r4) # R8 = no. of samples
    add(r4, r4, r4)  # 2 bytes per sample
    add(r0, r0, r4)
    mov(r10, r0) # R10 -> one sample after end of sample set

    ldr(r4, [r3, 4])
    mov(r12, r4)  # R12 = no. of coeffs
    sub(r4, 1)
    add(r4, r4, r4)
    add(r4, r4, r4)
    add(r2, r2, r4)  # r2 -> last coeff
    mov(r5, 4)  # Amount to inc/dec coeff pointer
    mov(r4, r11)  # Flags
    mov(r6, REVERSE)
    tst(r4, r6)
    itt(eq)  # If REVERSE not set, apply coeffs most recent first.
    mov(r9, r2)  # R9 -> last (most recent) coeff
    neg(r5, r5)
    vmov(s6, r5)

    mov(r5, r8)  # No of samples
    mov(r6, WRAP)
    tst(r4, r6)
    ittt(eq)  # If wrapping, r5 == no. of iterations
    mov(r6, r12) # Not wrapping: No. of coeffs
    sub(r5, r5, r6)  # If no wrap, no. to process = samples - coeffs + 1
    add(r5, 1)

    ldr(r4, [r3, 12])  # Decimate ( >= 1)
    cmp(r4, 1)
    it(mi)
    mov(r4, 1)  # Avoid crash if user set decimate == 0
    udiv(r5, r5, r4)
    vmov(s7, r5)  # No. of samples to process
    vmov(s10, r5)

    add(r4, r4, r4)  # 2 bytes per sample
    vmov(s9, r4)  # Bytes to decrement sample pointer

    ldr(r4, [r3, 16])  # Offset
    cmp(r4, 0)
    bmi(DOMEAN)  # -ve offset: calculate mean
    vmov(s1, r4)  # offset >= 0
    vcvt_f32_s32(s1, s1)  # S1 = provided offset
    b(DO_FILT)

# CALCULATE MEAN
    label(DOMEAN)
    # Point r0 to one after last sample
    vmov(r4, s5)  # Zero mean
    vmov(s1, r4)
    label(MEAN)
    sub(r0, 2)
    # get 16 bit sample and 0-extend. Note this works only for samples >= 0
    ldrh(r4, [r0, 0])
    vmov(s2, r4)
    vcvt_f32_s32(s2, s2)
    vadd(s1, s1, s2)
    cmp(r0, r7)  # sample set start
    bne(MEAN)
    vmov(s2, r8) # no. of samples
    vcvt_f32_s32(s2, s2)  # convert to float
    vdiv(s1, s1, s2)

# MEAN IS NOW IN S1
    label(DO_FILT)
    mov(r0, r10)
    sub(r0, 2)  # R0 -> last (most recent) sample
    vmov(r4, s7) # No. of results == no. of samples to be processed
    add(r4, r4, r4)  # 4 bytes per result
    add(r4, r4, r4)
    add(r1, r1, r4)  # R1: one after last result

    label(SAMPLE)
    sub(r1, 4)  # Point to result array
    # get 16 bit sample and 0-extend. Note this works only for samples >= 0
    ldrh(r4, [r0, 0])
    vmov(s2, r4)
    vcvt_f32_s32(s2, s2)

    vmov(r4, s5)  # Zero result register S3
    vmov(s3, r4)
# Set R2 coeff pointer to start / end and put update value in R3
    mov(r2, r9)  # R2 -> coeff[0] or coeff[last] depending on REVERSE
    vmov(r3, s6)  # Coeff pointer will inc/dec by 4

    mov(r6, r0)  # Current sample cidx
    mov(r5, r12) # no. of coeffs
    label(COEFF)
    vldr(s4, [r2, 0])  # get current coeff and point to next
    add(r2, r2, r3)  # (inc or dec by 4)

    # get 16 bit sample and 0-extend. Note this works only for samples >= 0
    ldrh(r4, [r6, 0])
    vmov(s2, r4)
    vcvt_f32_s32(s2, s2)  # Float sample value in s2
    vsub(s2, s2, s1)  # Subtract mean
    vmul(s2, s2, s4)  # Multiply coeff
    vadd(s3, s3, s2)  # Add into result
    sub(r6, 2)  # Point to next oldest sample

    cmp(r6, r7) # OK if current >= start
    bge(SKIP)
    # R6 -> before start
    mov(r6, r10)  # R6 -> one after sample set end
    sub(r6, 2) # R6 -> newest sample

    label(SKIP)
    sub(r5, 1)  # Decrement coeff counter
    bne(COEFF)

    vmul(s3, s3, s0)  # Scale
    vstr(s3, [r1, 0])  # Store in result array

    vmov(r4, s9)  # Bytes to decrement sample pointer
    sub(r0, r0, r4)

    vmov(r4, s7)
    sub(r4, 1)
    vmov(s7, r4)
    bne(SAMPLE)

    mov(r4, r11)  # Flags
    mov(r6, COPY)
    tst(r4, r6)
    beq(END)  # No copy back to source

# COPY BACK
    vmov(r1, s8)  # r1-> start of result array
    mov(r0, r7)  # r0 -> start of sample array
    vmov(r4, s10)  # No. of samples which were processed
    label(COPY_LOOP)
    vldr(s3, [r1, 0])  # Current result
    vadd(s3, s3, s1)  # Restore mean
    vcvt_s32_f32(s3, s3)  # Convert to integer
    vmov(r6, s3)
    strh(r6, [r0, 0])  # Store in IP array
    add(r0, 2)
    add(r1, 4)  # Next result
    sub(r4, 1)
    bgt(COPY_LOOP)
    vcvt_s32_f32(s3, s1)  # get mean
    vmov(r6, s3)
    mov(r4, r10)  # 1 sample after end
    label(COPY_LOOP_1)  # Set any uncomputed elements to mean
    cmp(r0, r4)
    bpl(END)
    strh(r6, [r0, 0])  # Store in IP array
    add(r0, 2)
    b(COPY_LOOP_1)

    label(END)
    pop({r8, r9, r10, r11, r12})
    vmov(r0, s10)

# Version where r0 -> array of float input samples
@micropython.asm_thumb
def dcf_fp(r0, r1, r2, r3):
    push({r8, r9, r10, r11, r12})
    # Populate registers
    vmov(s8, r1)
    ldr(r4, [r3, 8])
    mov(r11, r4)  # R11 = Flags
    mov(r7, SCALE)
    tst(r4, r7)
    ittte(eq)
    mov(r5, 1)  # No scale factor: s0 = 1.0
    vmov(s0, r5)
    vcvt_f32_s32(s0, s0)
    vldr(s0, [r1, 0])  # S0 = scaling factor from op array

    mov(r4, 0)
    vmov(s5, r4)
    vcvt_f32_s32(s5, s5)  # S5 = 0.0

    mov(r7, r0)  # R7 -> sample set start
    mov(r9, r2)  # R9 -> coeff start

    ldr(r4, [r3, 0])
    mov(r8, r4) # R8 = no. of samples
    add(r4, r4, r4)  # 4 bytes per sample
    add(r4, r4, r4)
    add(r0, r0, r4)
    mov(r10, r0) # R10 -> one sample after end of sample set

    ldr(r4, [r3, 4])
    mov(r12, r4)  # R12 = no. of coeffs
    sub(r4, 1)
    add(r4, r4, r4)
    add(r4, r4, r4)
    add(r2, r2, r4)  # r2 -> last coeff
    mov(r5, 4)  # Amount to inc/dec coeff pointer
    mov(r4, r11)  # Flags
    mov(r6, REVERSE)
    tst(r4, r6)
    itt(eq)  # If REVERSE not set, apply coeffs most recent first.
    mov(r9, r2)  # R9 -> last (most recent) coeff
    neg(r5, r5)
    vmov(s6, r5)

    mov(r5, r8)  # No of samples
    mov(r6, WRAP)
    tst(r4, r6)
    ittt(eq)  # If wrapping, r5 == no. of iterations
    mov(r6, r12) # Not wrapping: No. of coeffs
    sub(r5, r5, r6)  # If no wrap, no. to process = samples - coeffs + 1
    add(r5, 1)

    ldr(r4, [r3, 12])  # Decimate ( >= 1)
    cmp(r4, 1)
    it(mi)
    mov(r4, 1)  # Avoid crash if user set decimate == 0
    udiv(r5, r5, r4)
    vmov(s7, r5)  # No. of samples to process
    vmov(s10, r5)

    add(r4, r4, r4)  # 4 bytes per sample
    add(r4, r4, r4)
    vmov(s9, r4)  # Bytes to decrement sample pointer

    ldr(r4, [r3, 16])  # Offset
    cmp(r4, 0)
    bmi(DOMEAN)  # -ve offset: calculate mean
    vmov(s1, r4)  # offset >= 0
    vcvt_f32_s32(s1, s1)  # S1 = provided offset
    b(DO_FILT)

# CALCULATE MEAN
    label(DOMEAN)
    # R0 points to one after last sample
    vmov(r4, s5)  # Zero mean
    vmov(s1, r4)
    label(MEAN)
    sub(r0, 4)
    # get sample
    vldr(s2, [r0, 0])
    vadd(s1, s1, s2)
    cmp(r0, r7)  # sample set start
    bne(MEAN)
    vmov(s2, r8) # no. of samples
    vcvt_f32_s32(s2, s2)  # convert to float
    vdiv(s1, s1, s2)

# MEAN IS NOW IN S1
    label(DO_FILT)
    mov(r0, r10)
    sub(r0, 4)  # R0 -> last (most recent) sample
    vmov(r4, s7) # No. of results == no. of samples to be processed
    add(r4, r4, r4)  # 4 bytes per result
    add(r4, r4, r4)
    add(r1, r1, r4)  # R1: one after last result

    label(SAMPLE)
    sub(r1, 4)  # Point to result array
    # get sample
    vldr(s2, [r0, 0])

    vmov(r4, s5)  # Zero result register S3
    vmov(s3, r4)
# Set R2 coeff pointer to start / end and put update value in R3
    mov(r2, r9)  # R2 -> coeff[0] or coeff[last] depending on REVERSE
    vmov(r3, s6)  # Coeff pointer will inc/dec by 4

    mov(r6, r0)  # Current sample cidx
    mov(r5, r12) # no. of coeffs
    label(COEFF)
    vldr(s4, [r2, 0])  # get current coeff and point to next
    add(r2, r2, r3)  # (inc or dec by 4)

    vldr(s2, [r6, 0])  # get current sample
    vsub(s2, s2, s1)  # Subtract mean
    vmul(s2, s2, s4)  # Multiply coeff
    vadd(s3, s3, s2)  # Add into result
    sub(r6, 4)  # Point to next oldest sample

    cmp(r6, r7) # OK if current >= start
    bge(SKIP)
    # R6 -> before start
    mov(r6, r10)  # R6 -> one after sample set end
    sub(r6, 4) # R6 -> newest sample

    label(SKIP)
    sub(r5, 1)  # Decrement coeff counter
    bne(COEFF)

    vmul(s3, s3, s0)  # Scale
    vstr(s3, [r1, 0])  # Store in result array

    vmov(r4, s9)  # Bytes to decrement sample pointer
    sub(r0, r0, r4)

    vmov(r4, s7)
    sub(r4, 1)
    vmov(s7, r4)
    bne(SAMPLE)

    mov(r4, r11)  # Flags
    mov(r6, COPY)
    tst(r4, r6)
    beq(END)  # No copy back to source

# COPY BACK
    vmov(r1, s8)  # r1-> start of result array
    mov(r0, r7)  # r0 -> start of sample array
    vmov(r4, s10)  # No. of samples which were processed
    label(COPY_LOOP)
    vldr(s3, [r1, 0])  # Current result
    vadd(s3, s3, s1)  # Restore mean
    vstr(s3, [r0, 0])  # Store
    add(r0, 4)
    add(r1, 4)  # Next result
    sub(r4, 1)
    bgt(COPY_LOOP)
    mov(r4, r10)  # 1 sample after end
    label(COPY_LOOP_1)  # Set any uncomputed elements to mean
    cmp(r0, r4)
    bpl(END)
    vstr(s1, [r0, 0])  # Store mean in I/P array
    add(r0, 4)
    b(COPY_LOOP_1)

    label(END)
    pop({r8, r9, r10, r11, r12})
    vmov(r0, s10)
