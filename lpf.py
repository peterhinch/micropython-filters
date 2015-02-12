# Demo program for FIR filter module
# Author: Peter Hinch
# 12th Feb 2015
# Outputs a swept frequency sine wave on Dac1
# Timer interrupt reads the analog input, filters it, and outputs the result on Dac 2.
# Requires a link between X5 and X7

import math
import pyb
import array
from fir import fir
import micropython
micropython.alloc_emergency_exception_buf(100)

# Define hardware
dac1 = pyb.DAC(1)
dac2 = pyb.DAC(2)
adc  = pyb.ADC("X7")
tim = pyb.Timer(4, freq=2000) # Sampling freq 10KHz is about the limit 14KHz without constraint

# Data for FIR filter Pass (@2Ksps) 0-40Hz Stop 80Hz->
coeffs = array.array('i', (72, 47, 61, 75, 90, 105, 119, 132, 142, 149, 152, 149,
  140, 125, 102, 71, 33, -12, -65, -123, -187, -254, -322, -389, -453, -511, -561,
  -599, -622, -628, -615, -579, -519, -435, -324, -187, -23, 165, 375, 607, 855,
  1118, 1389, 1666, 1941, 2212, 2472, 2715, 2938, 3135, 3303, 3437, 3535, 3594,
  3614, 3594, 3535, 3437, 3303, 3135, 2938, 2715, 2472, 2212, 1941, 1666, 1389,
  1118, 855, 607, 375, 165, -23, -187, -324, -435, -519, -579, -615, -628, -622,
  -599, -561, -511, -453, -389, -322, -254, -187, -123, -65, -12, 33, 71, 102, 125,
  140,  149, 152, 149, 142, 132, 119, 105, 90, 75, 61, 47, 72))
ncoeffs = len(coeffs)
data = array.array('i', [0]*(ncoeffs +3)) # Scratchpad must be three larger than coeffs
data[0] = ncoeffs
data[1] = 16

# Data input, filter and output
# The constraint is a convenience to ensure that any inadvertent overflow shows as
# clipping on the 'scope. If you get the scaling right you can eliminate it...
def cb(timer):
    val = fir(data, coeffs, adc.read()) // 16 # Filter amd scale
    dac2.write(max(0, min(255, val))) # Constrain, shift (no DC from bandpass) and output

tim.callback(cb)

# Sweep generator
def sine_sweep(start, end, mult):     # Emit sinewave on DAC1
    buf = bytearray(100)
    for i in range(len(buf)):
        buf[i] = 128 + int(110 * math.sin(2 * math.pi * i / len(buf)))

    freq = start
    while True:
        dac1.write_timed(buf, int(freq) * len(buf), mode=pyb.DAC.CIRCULAR)
        print(freq, "Hz")
        pyb.delay(2500)
        freq *= mult
        if freq > end:
            freq = start

sine_sweep(10, 400, 1.33)

