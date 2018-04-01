# autocorrelate.py

# Generates Python code providing a binary signal having good autocorrelation
# characteristics. These comprise
# 1. An autocorrelation function approximating an impulse function.
# 2. A limited maximum runlength (i.e. limited bandwidth).
# 3. Zero DC component (no. of 1's == no. of zeros)
# Note that specifying a large maximum runlength will probably result in an
# actual runlength which is much shorter: the process is stochastic and long
# runlengths are rare.

# The Python code produced instantiates the following variables corresponding
# to the best result achieved.
# data a list of data values: these are 1 or -1
# detection_ratio The autocorrelation detection ratio.
# runlength The actual maximum runlength (<= the specified RL).

import utime
import pyb
from array import array
from filt import dcf, WRAP, SCALE, REVERSE

# Return the greatest runlength in a buffer
def runlength(bufin):
    max_rl = 1
    rl = 1
    last_bit = bufin[0]
    for bit in bufin[1:]:
        if bit == last_bit:
            rl += 1
            max_rl = max(rl, max_rl)
        else:
            last_bit = bit
            rl = 1
    return max_rl

def make_sample(bufin, coeffs, siglen, max_rl):
    while True:
        for x in range(siglen):
            bufin[x] = 3048 if pyb.rng() & 1 else 1048  # range 2048+-1000

        if sum(bufin) - 2048 * siglen == 0:  # No DC component
            if runlength(bufin) <= max_rl:  # RL meets criterion
                for x in range(siglen):
                    # Autocorrelation: coeffs == signal
                    coeffs[x] = (bufin[x] - 2048) / 1000  # range +-1
                return

def main(filename='/sd/samples.py', runtime=60, siglen=50, max_rl=6):
    if siglen % 2 == 1:
        print('Signal length must be even to meet zero DC criterion.')
        return
    # Setup for correlation
    setup = array('i', (0 for _ in range(5))) 
    setup[0] = siglen  # Input buffer length
    setup[1] = siglen  # Coefficient buffer length
    setup[2] = WRAP | SCALE # Normal time order.
    setup[3] = 0 # No copy back: I/P sample set unchanged
    setup[4] = 2048  # Offset
    with open(filename, 'w') as f:
        f.write('# Code produced by autocorrelate.py\n')
        f.write('# Each list element comprises [[data...], detection_rato]\n')
        f.write('signal_length = {:d}\n'.format(siglen))
        f.write('max_run_length = {:d}\n'.format(max_rl))
        f.write('signals = [\n')
    bufin = array('H', (0 for i in range(siglen)))
    op = array('f', (0 for _ in range(siglen)))
    coeffs = array('f', (0 for _ in range(siglen)))

    start = utime.time()
    end = start + runtime
    det_ratio = 0  # Best detection ratio so far
    while utime.time() < end:
        # Populate bufin and coeffs with a signal
        #  meeting runlength and DC criteria
        make_sample(bufin, coeffs, siglen, max_rl)
        op[0] = 0.001 # Scale
        n_results = dcf(bufin, op, coeffs, setup)

        maxop = op[siglen -1]  # Highest correlation is always last sample
        nextop = 0  # next highest (i.e. worst invalid) correlation
        for x in range(n_results):
            res = op[x]
            if res < maxop and res > nextop:
                nextop = res
        dr = maxop/nextop if nextop != 0 else maxop # ????
        if dr > det_ratio:  # new best candidate
            det_ratio = dr
            for x in range(n_results):
                res = op[x]
                print('{:3d}  {:8.1f}'.format(x, res))
            s = 'Max correlation {:5.1f} Next largest {:5.1f} Detection ratio {:5.1f}.'
            print(s.format(maxop, nextop, maxop/nextop))
            print('runtime (secs)', (utime.time() - start))
            el_count = 0
            with open(filename, 'a') as f:
                f.write('[[')
                for x in bufin:
                    f.write(str(int((x -2048)/1000)))
                    f.write(',')
                    el_count += 1
                    el_count %= 16
                    if el_count == 0:
                        f.write('\n')
                f.write('],{:5.1f}, {:d}],\n'.format(dr, runlength(bufin)))

    with open(filename, 'a') as f:
        f.write(']\n')
        f.write('data, detection_ratio, runlength = signals[-1]\n')

#main(filename = '/sd/rl_2.py', runtime=600, max_rl = 2)
main(filename = '/sd/rl_3.py', runtime=600, max_rl = 3)
#main()
