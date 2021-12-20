# Test functions for FIR filter
# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

import array
from time import ticks_us, ticks_diff
from fir import fir

# Coefficient options
# 41 tap low pass filter, 2dB ripple 60dB stop
c = [-176, -723, -1184, -868, 244, 910, 165, -1013, -693,
  977, 1398, -615, -2211, -257, 3028, 1952, -3729, -5500,
  4201, 20355, 28401, 20355, 4201, -5500, -3729, 1952,
  3028, -257, -2211, -615, 1398, 977, -693, -1013, 165,
  910, 244, -868, -1184, -723, -176]

# 21 tap LPF
d = [-1318, -3829, -4009, -717, 3359, 2177, -3706, -5613, 4154, 20372, 28471, 20372, 4154, -5613, -3706,
  2177, 3359, -717, -4009, -3829, -1318]
# 109 tap LPF
e = [-24, 89, 69, 78, 95, 115, 135, 154, 171, 185, 196, 202, 201,
  194, 178, 155, 122, 81, 31, -26, -91, -160, -232, -306, -378,
  -446, -506, -555, -591, -610, -608, -584, -535, -460, -357,
  -225, -66, 121, 333, 568, 823, 1094, 1375, 1663, 1952, 2237,
  2510, 2768, 3004, 3213, 3391, 3534, 3638, 3702, 3723, 3702,
  3638, 3534, 3391, 3213, 3004, 2768, 2510, 2237, 1952, 1663,
  1375, 1094, 823, 568, 333, 121, -66, -225, -357, -460, -535,
  -584, -608, -610, -591, -555, -506, -446, -378, -306, -232,
  -160, -91, -26, 31, 81, 122, 155, 178, 194, 201, 202, 196,
  185, 171, 154, 135, 115, 95, 78, 69, 89, -24]

# Initialisation
coeffs = array.array('i', d)
ncoeffs = len(coeffs)
data = array.array('i', [0]*(ncoeffs +3))
data[0] = ncoeffs
data[1] = 1             # Try a single bit shift

def test():             # Impulse response replays coeffs*impulse_size >> scale
    print(fir(data, coeffs, 100))
    for n in range(len(coeffs)+3):
        print(fir(data, coeffs, 0))

def timing():           # Test removes overhead of pyb function calls
    t = ticks_us()
    fir(data, coeffs, 100)
    t1 = ticks_diff(ticks_us(), t)
    t = ticks_us()
    fir(data, coeffs, 100)
    fir(data, coeffs, 100)
    t2 = ticks_diff(ticks_us(), t)
    print(t2-t1,"uS")
# Results: 14uS for a 21 tap filter, 16uS for 41 taps, 23uS for 109 (!)
# Time = 12 + 0.102N uS where N = no. of taps

test()
print("Done! Timing:")
timing()

