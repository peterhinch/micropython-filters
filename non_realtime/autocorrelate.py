# autocorrelate.py

# Released under the MIT licence.
# Copyright Peter Hinch 2018

# Generates Python code providing a binary signal having good autocorrelation
# characteristics. These comprise:
# 1. An autocorrelation function approximating an impulse function.
# 2. A limited maximum runlength (i.e. limited bandwidth).
# 3. Zero DC component (no. of 1's == no. of zeros)
# Note that specifying a large maximum runlength will probably result in an
# actual runlength which is much shorter: the process is stochastic and long
# runlengths are rare.

# The Python code produced instantiates the following variables corresponding
# to the best result achieved.
# data a list of data values: these are 1 or -1.
# detection_ratio: (value at actual match)/(next highest value)
# runlength The actual maximum runlength (<= the specified RL).

# A random sequence of N values constrained to +1 or -1 is generated which meets
# the RL and zero DC requirements.
# The coefficients are set to that sequence (autocorrelation).
# The input data sequence is N zeros followed by the sequence.
# Linear cross correlation is performed and the performance checked.
# The current best sequence is written to file.

import utime
import pyb
from array import array
from filt import dcf_fp, WRAP, SCALE, REVERSE

def make_sample(bufin, coeffs, siglen, max_rl):
    actual_max_rl = 0
    while True:
        rl = 0
        for x in range(siglen):
            bit = 1 if pyb.rng() & 1 else -1
            if rl < max_rl:
                coeffs[x] = bit
                last_bit = bit
                if rl > actual_max_rl:
                    actual_max_rl = rl
                rl += 1
            else:
                last_bit *= -1
                coeffs[x] = last_bit
                rl = 1

        if sum(coeffs) == 0:  # No DC component
            # Signal is N zeros followed by N values of +-1
            # For autocorrelation signal == coeffs
            for x in range(siglen):
                bufin[x] = 0
            for x in range(siglen):
                bufin[x + siglen] = coeffs[x] # range +-1
            return actual_max_rl

def main(filename='/sd/samples.py', runtime=60, siglen=50, max_rl=6):
    if siglen % 2 == 1:
        print('Signal length must be even to meet zero DC criterion.')
        return
    if max_rl < 2:
        print('Max runlength must be >= 2.')
        return
    # Setup for correlation
    setup = array('i', (0 for _ in range(5))) 
    setup[0] = 2 * siglen  # Input buffer length
    setup[1] = siglen  # Coefficient buffer length
    setup[2] = 0  # Normal time order. No wrap. No copy back: I/P sample set unchanged
    setup[3] = 1  # No decimation.
    setup[4] = 0  # No offset.
    with open(filename, 'w') as f:
        f.write('# Code produced by autocorrelate.py\n')
        f.write('# Each list element comprises [[data...], detection_rato, runlength]\n')
        f.write('# where runlength is the actual maximum RL in the signal.\n')
        f.write('# Variables data, detection_ratio and runlength hold the values\n')
        f.write('# for the best detection_ratio achieved.\n')
        f.write('signal_length = {:d}\n'.format(siglen))
        f.write('max_run_length = {:d}\n'.format(max_rl))
        f.write('signals = [\n')
    bufin = array('f', (0 for i in range(2*siglen)))
    op = array('f', (0 for _ in range(2*siglen)))
    coeffs = array('f', (0 for _ in range(siglen)))

    start = utime.time()
    end = start + runtime
    count = 0  # Candidate count
    last_best = siglen  # Count of mismatched bits in worst invalid detection
    det_ratio = 0  # Detection ratio: (value at actual match)/(next highest value)
    while utime.time() < end:
        # Populate bufin and coeffs with a signal
        # meeting runlength and zero DC criteria
        actual_rl = make_sample(bufin, coeffs, siglen, max_rl)
        count += 1
        n_results = dcf_fp(bufin, op, coeffs, setup)

        maxop = max(op)  # Highest correlation
        nextop = 0  # next highest (i.e. worst invalid) correlation
        for x in range(n_results):
            res = op[x]
            if res < maxop and res > nextop:
                nextop = res
        if nextop < last_best:  # new best candidate
            last_best = nextop
            for x in range(n_results):
                res = op[x]
                print('{:3d}  {:8.1f}'.format(x, res))
            s = 'Max correlation {:5.1f} Next largest {:5.1f} Detection ratio {:5.1f}.'
            print(s.format(maxop, nextop, maxop/nextop))
            print('runtime (secs)', (utime.time() - start))
            el_count = 0
            with open(filename, 'a') as f:
                f.write('[[')
                for x in coeffs:
                    f.write(str(int(x)))  # 1 or -1
                    f.write(',')
                    el_count += 1
                    el_count %= 16
                    if el_count == 0:
                        f.write('\n')
                # Note that actual max runlength can be < specified value
                # so write out actual value.
                det_ratio = maxop/nextop if nextop != 0 else 0  # Pathological data ??
                f.write('],{:5.1f}, {:d}],\n'.format(det_ratio, actual_rl))

    with open(filename, 'a') as f:
        f.write(']\n')
        f.write('data, detection_ratio, runlength = signals[-1]\n')
    fstr = 'Best detection ratio achieved: {:5.1f} match {:5.1f} mismatch {:5.1f}'
    print(fstr.format(det_ratio, maxop, last_best))
    print('rl == {:d} patterns tested {:4d}.'.format(max_rl, count))

# rl == 2 yielded det ratio 10 (50/10 == 5 bits match) in 71s of 15 min run
# main(filename = '/sd/rl_2.py', runtime=900, max_rl = 2)
# Let it rip with any runlength and analyse the results afterwards:
# best ratio was 12.5 with rl == 6
#main(filename = '/sd/rl_any.py', runtime=3600, max_rl = 25)
# Find best rl <= 3 sequence yielded det ratio 10
#main(filename = '/sd/rl_3.py', runtime=60, max_rl = 3)
# Find best rl <= 6 sequence
main()
