# Demo program for moving average filter
# Author: Peter Hinch
# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch
# 16th Dec 2021

import array
from time import ticks_us, ticks_diff
# from avg_pico import avg
from avg import avg

data = array.array('i', [0]*13) # Average over ten samples
data[0] = len(data)

def test():
    for x in range(12):
        print(avg(data, 1000))
    for x in range(12):
        print(avg(data, 0))

def timing():
    t = ticks_us()
    avg(data, 10)
    t1 = ticks_diff(ticks_us(), t)  # Time for one call with timing overheads
    t = ticks_us()
    avg(data, 10)
    avg(data, 10)
    t2 = ticks_diff(ticks_us(), t)  # Time for two calls with timing overheads
    print(t2-t1,"uS")           # Time to execute the avg() call

test()
print("Timing test")
timing()

