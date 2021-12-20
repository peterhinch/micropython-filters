# Demo program for moving average filter
# Author: Peter Hinch
# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch
# 16th Dec 2021

import array
from time import ticks_us, ticks_diff
from avg_pico import avg

data = array.array('i', (0 for _ in range(19))) # Average over 16 samples
data[0] = len(data)

def test():
    for x in range(16):
        print(avg(data, 1000, 4))  # Scale by 4 bits (divide by 16)
    for x in range(18):
        print(avg(data, 0, 4))

def timing():
    t = ticks_us()
    avg(data, 10, 4)
    t1 = ticks_diff(ticks_us(), t)  # Time for one call with timing overheads
    t = ticks_us()
    avg(data, 10, 4)
    avg(data, 10, 4)
    t2 = ticks_diff(ticks_us(), t)  # Time for two calls with timing overheads
    print(t2-t1,"uS")           # Time to execute the avg() call

test()
print("Timing test")
timing()

