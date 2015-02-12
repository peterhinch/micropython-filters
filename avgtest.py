# Demo program for moving average filter
# Author: Peter Hinch
# 12th Feb 2015
import array, pyb
from avg import avg

data = array.array('i', [0]*13) # Average over ten samples
data[0] = len(data)

def test():
    for x in range(12):
        print(avg(data, 1000))
    for x in range(12):
        print(avg(data, 0))

def timing():
    t = pyb.micros()
    avg(data, 10)
    t1 = pyb.elapsed_micros(t)  # Time for one call with timing overheads
    t = pyb.micros()
    avg(data, 10)
    avg(data, 10)
    t2 = pyb.elapsed_micros(t)  # Time for two calls with timing overheads
    print(t2-t1,"uS")           # Time to execute the avg() call

test()
print("Timing test")
timing()

