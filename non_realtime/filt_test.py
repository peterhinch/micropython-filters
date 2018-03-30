# filt_test.py Test/demo program for filt.py

# Released under the MIT licence.
# Copyright Peter Hinch 2018

# This program simulates the acquisition of an array of samples on a Pyboard ADC
# using read_timed. The received signal is a sinewave biassed to lie in the
# middle of the ADC voltage range. Two FIR filters are applied.
# The first is a low pass filter which extracts the DC bias level.
# The second is a bandpass filter which extracts the signal. The passband is
# centred on a frequency corresponding to 8 cycles in the input buffer. The
# rejection characteristics may be demonstrated by altering the value of
# NCYCLES - try a value of 6 or 12.
# See coeffs.py for bandpass filter characteristics.

from array import array
from coeffs import coeffs_8a, coeffs_0
from math import sin, pi
import utime
from filt import dcf, WRAP, SCALE, REVERSE, COPY

RBUFLEN = 128
# Number of cycles in input buffer. 8 == centre of passband of coeffs_8a.
NCYCLES = 8
cycles = RBUFLEN / NCYCLES

bufin = array('H', (2048 + int(1500 * sin(2 * cycles * pi * i / RBUFLEN)) for i in range(RBUFLEN)))
setup = array('i', (0 for _ in range(5)))
op = array('f', (0 for _ in range(RBUFLEN)))

# This filter extracts a DC level in presence of noise
# Wrap because signal sought (DC) is constant.
setup[0] = len(bufin)
setup[1] = len(coeffs_0)
setup[2] = WRAP | SCALE
setup[3] = 1 # Decimate by 1
setup[4] = 0 # zero offset
op[0] = 0.967 # Scale
dcf(bufin, op, coeffs_0, setup)
print('DC', sum(op)/len(op))

# This is a bandpass filter centred on a frequency such that the
# input sample array contains 8 full cycles
setup[0] = len(bufin)
setup[1] = len(coeffs_8a)
setup[2] = SCALE | COPY
setup[3] = 1 # Decimate
setup[4] = -1 # offset == -1: calculate mean
op[0] = 1.037201

t = utime.ticks_us()
n_results = dcf(bufin, op, coeffs_8a, setup)
t = utime.ticks_diff(utime.ticks_us(), t)
print('No. of results =', n_results)

print('Sample      O/P   input buffer')
for i in range(n_results):
    print('{:3d}    {:8.1f}      {:5d}'.format(i, op[i], bufin[i]))
print('Duration {:5d}μs'.format(t))


