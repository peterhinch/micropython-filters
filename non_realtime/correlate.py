# correlate.py Demo of retrieving signal buried in noise

# Released under the MIT licence.
# Copyright Peter Hinch 2018

# This simulates a Pyboard ADC acquiring a signal using read_timed. The signal is
# digital (switching between two fixed voltages) but is corrupted by a larger analog
# noise source.
# The output array contains the correlation of the corrupted input with the known
# expected signal.
# A successful detection comprises a uniquely large value at sample 930 where the
# end of the signal is located. The program also outputs the second largest
# correlation value and the ratio of the two as a measure of the certainty of
# detection.

# The chosen signal is a pseudo-random digital burst. This was chosen because the
# auto-correlation function of random noise is an impulse function.
# The module autocorrelate.py was used to generate this

# In this test it is added to a pseudo-random analog signal of much longer
# duration to test the reliability of discriminaton.

import utime
import pyb
from array import array
from filt import dcf, WRAP, SCALE, REVERSE
# Read buffer length
RBUFLEN = 1000
# Digital amplitude. Compares with analog amplitude of 1000.
DIGITAL_AMPLITUDE = 600  # 400 is about the limit with occasional false positives

def rn_analog():  # Random number in range +- 1000
    return int(pyb.rng() / 536870 - 1000)

# Data produced by autocorrelate.py
# signal length = 50 The longer this is the greater the probability of detection.
# Actual max runlength = 6 DIGITAL_AMPLITUDE 600 gave DR of ~2.4
#signal = bytearray([-1,-1,1,1,-1,1,-1,-1,1,-1,1,-1,1,1,1,1,
#-1,1,-1,1,-1,-1,-1,-1,-1,-1,1,1,1,-1,-1,1,
#1,1,-1,1,1,1,-1,1,1,-1,-1,1,-1,-1,1,-1,
#1,-1,])

# Actual max runlength 3 DIGITAL_AMPLITUDE 600 gave DR of ~2.2
# in repeated (> 70) runs lowest DR seen was 1.3, with no false positives.
signal = bytearray([-1,-1,1,1,-1,-1,1,1,-1,1,-1,1,1,-1,1,-1,
-1,-1,1,1,-1,1,1,-1,1,1,1,-1,-1,1,-1,-1,
1,1,-1,-1,-1,1,-1,1,1,-1,1,1,-1,-1,1,-1,
1,-1,])
siglen = len(signal)

# Input buffer contains random noise. While this is a simulation, the bias of 2048
# emulates a Pyboard ADC biassed at its mid-point (1.65V).
# Order (as from read_timed) is oldest first.
bufin = array('H', (2048 + rn_analog() for i in range(RBUFLEN)))  # range 2048 +- 1000

# Add signal in. Burst ends 20 samples before the end.
x = RBUFLEN - siglen - 20
for s in signal:
    s = 1 if s == 1 else -1
    bufin[x] += s * DIGITAL_AMPLITUDE
    x += 1

# Coeffs hold the expected signal in normal time order (oldest first).
coeffs = array('f', (1 if signal[i] == 1 else -1 for i in range(siglen)))  # range +-1

op = array('f', (0 for _ in range(RBUFLEN)))
setup = array('i', [0]*5) 
setup[0] = len(bufin)
setup[1] = len(coeffs)
setup[2] = SCALE  # No wrap, normal time order.
setup[3] = 0 # No copy back: I/P sample set unchanged
setup[4] = 2048  # Offset
op[0] = 0.001 # Scale
t = utime.ticks_us()
n_results = dcf(bufin, op, coeffs, setup)
t = utime.ticks_diff(utime.ticks_us(), t)

ns = 0
maxop = 0
for x in range(n_results):
    res = op[x]
    print('{:3d}  {:8.1f}'.format(x, res))
    if res > maxop:
        maxop = res
        ns = x  # save sample no.
nextop = 0
for x in op:
    if x < maxop and x > nextop:
        nextop = x
s = 'Max correlation {:5.1f} at sample {:d} Next largest {:5.1f} Detection ratio {:5.1f}.'
print(s.format(maxop, ns, nextop, maxop/nextop))
if ns == 930:
    print('Correct detection.')
else:
    print('FALSE POSITIVE.')
print('Duration {:5d}μs'.format(t))
