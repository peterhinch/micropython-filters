# filt_test_all.py
# Test suite for filt.py non-realtime inline assembler routines.
# Run on Pyboard.

# Released under the MIT licence.
# Copyright Peter Hinch 2018

from array import array
from filt import dcf, dcf_fp, WRAP, SCALE, REVERSE, COPY
SIGLEN = const(32)

# Setup common to all tests
setup = array('i', (0 for _ in range(5))) 
setup[0] = 2 * SIGLEN  # Input buffer length
setup[1] = SIGLEN  # Coefficient buffer length

# Basic test
def test1():
    exp = [0.0,-1.0,-2.0,-3.0,-4.0,-5.0,-6.0,-7.0,-8.0,-9.0,-10.0,-11.0,-12.0,-13.0,-14.0,
           -15.0,-16.0,-13.0,-10.0,-7.0,-4.0,-1.0,2.0,5.0,8.0,11.0,14.0,17.0,20.0,23.0,26.0,
           29.0,32.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

    setup[2] = 0  # Normal time order. No wrap.
    setup[3] = 1  # No decimation
    setup[4] = 0  # Offset
    bufin = array('f', (0 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = coeff
        idx += 1
    n_results = dcf_fp(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(op):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN + 1:
        print('Siglen fail')
        ok = False
    return ok

# Test Decimation
def test2():
    exp = [-4.0,-8.0,-12.0,-16.0,-4.0,8.0,20.0,32.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,]

    setup[2] = 0  # Normal time order. No wrap.
    setup[3] = 4  # Decimation by 4
    setup[4] = 0  # No offset
    bufin = array('f', (0 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = coeff
        idx += 1
    n_results = dcf_fp(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(op):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN // 4:  # Decimation factor
        print('Siglen fail')
        ok = False
    return ok

# Test copy
def test3():
    exp = [0.0,-1.0,-2.0,-3.0,-4.0,-5.0,-6.0,-7.0,-8.0,-9.0,-10.0,-11.0,-12.0,-13.0,-14.0,
           -15.0,-16.0,-13.0,-10.0,-7.0,-4.0,-1.0,2.0,5.0,8.0,11.0,14.0,17.0,20.0,23.0,26.0,
           29.0,32.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

    setup[2] = COPY  # Normal time order. Copy.
    setup[3] = 1  # No decimation
    setup[4] = 0  # No offset
    bufin = array('f', (0 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = coeff
        idx += 1
    n_results = dcf_fp(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(op):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN + 1:
        print('Siglen fail')
        ok = False
    return ok

# Test wrap
def test4():
    exp = [29.0,26.0,23.0,20.0,17.0,14.0,11.0,8.0,5.0,2.0,-1.0,-4.0,-7.0,-10.0,
           -13.0,-16.0,-15.0,-14.0,-13.0,-12.0,-11.0,-10.0,-9.0,-8.0,-7.0,-6.0,
           -5.0,-4.0,-3.0,-2.0,-1.0,0.0,-1.0,-2.0,-3.0,-4.0,-5.0,-6.0,-7.0,-8.0,
           -9.0,-10.0,-11.0,-12.0,-13.0,-14.0,-15.0,-16.0,-13.0,-10.0,-7.0,-4.0,
           -1.0,2.0,5.0,8.0,11.0,14.0,17.0,20.0,23.0,26.0,29.0,32.0,]

    setup[2] = WRAP
    setup[3] = 1  # No decimation
    setup[4] = 0  # No offset
    bufin = array('f', (0 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = coeff
        idx += 1
    n_results = dcf_fp(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(op):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN * 2 :
        print('Siglen fail')
        ok = False
    return ok

# Test reverse
def test5():
    exp = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,16.0,
           13.0,10.0,7.0,4.0,1.0,-2.0,-5.0,-8.0,-11.0,-14.0,-17.0,-20.0,-23.0,-26.0,
           -29.0,-32.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
           0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,]

    setup[2] = REVERSE
    setup[3] = 1  # No decimation
    setup[4] = 0  # No offset
    bufin = array('f', (0 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = coeff
        idx += 1
    n_results = dcf_fp(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(op):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN + 1:
        print('Siglen fail')
        ok = False
    return ok

# ***** dcf tests *****
# Normal time order, scale and copy back
def test6():
    exp = [2048,2047,2046,2045,2044,2043,2042,2041,2040,2039,2038,2037,2036,2035,
          2034,2033,2032,2035,2038,2041,2044,2047,2050,2053,2056,2059,2062,2065,
          2068,2071,2074,2077,2080,2048,2048,2048,2048,2048,2048,2048,2048,2048,
          2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,
          2048,2048,2048,2048,2048,2048,2048,2048]

    setup[2] = SCALE | COPY
    setup[3] = 1  # No decimation
    setup[4] = 2048  # Offset
    bufin = array('H', (2048 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    op[0] = 0.001  # Scaling
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = int(2048 + 1000 * coeff)
        idx += 1
    n_results = dcf(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(bufin):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN + 1:
        print('Siglen fail')
        ok = False
    return ok

# Reverse time order
def test7():
    exp = [2048,2049,2050,2051,2052,2053,2054,2055,2056,2057,2058,2059,2060,2061,
           2062,2063,2064,2061,2058,2055,2052,2049,2046,2043,2040,2037,2034,2031,
           2028,2025,2022,2019,2016,2048,2048,2048,2048,2048,2048,2048,2048,2048,
           2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,
           2048,2048,2048,2048,2048,2048,2048,2048]

    setup[2] = SCALE | COPY | REVERSE
    setup[3] = 1  # No decimation
    setup[4] = 2048  # Offset
    bufin = array('H', (2048 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    op[0] = 0.001  # Scaling
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = int(2048 + 1000 * coeff)
        idx += 1
    n_results = dcf(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(bufin):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN + 1:
        print('Siglen fail')
        ok = False
    return ok

# Circular convolution
def test8():
    exp = [2077,2074,2071,2068,2065,2062,2059,2056,2053,2050,2047,2044,2041,
           2038,2035,2032,2033,2034,2035,2036,2037,2038,2039,2040,2041,2042,
           2043,2044,2045,2046,2047,2048,2047,2046,2045,2044,2043,2042,2041,
           2040,2039,2038,2037,2036,2035,2034,2033,2032,2035,2038,2041,2044,
           2047,2050,2053,2056,2059,2062,2065,2068,2071,2074,2077,2080,]

    setup[2] = SCALE | COPY | WRAP
    setup[3] = 1  # No decimation
    setup[4] = 2048  # Offset
    bufin = array('H', (2048 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    op[0] = 0.001  # Scaling
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = int(2048 + 1000 * coeff)
        idx += 1
    n_results = dcf(bufin, op, coeffs, setup)
    ok = True
    for idx, x in enumerate(bufin):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != 2 * SIGLEN:
        print('Siglen fail')
        ok = False
    return ok

# Decimation test
def test9():
    exp = [2044,2040,2036,2032,2044,2056,2068,2080,2048,2048,2048,2048,2048,
           2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,
           2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,
           2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,
           2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,2048,]

    setup[2] = SCALE | COPY
    setup[3] = 4  # Decimation
    setup[4] = -1  # Offset
    bufin = array('H', (2048 for i in range(2*SIGLEN)))
    op = array('f', (0 for _ in range(2*SIGLEN)))
    op[0] = 0.001  # Scaling
    coeffs = array('f', (-1 if x < SIGLEN/2 else 1 for x in range(SIGLEN)))
    idx = SIGLEN
    for coeff in coeffs:
        bufin[idx] = int(2048 + 1000 * coeff)
        idx += 1
    n_results = dcf(bufin, op, coeffs, setup)
    ok = True
    #print(n_results)
    #print('[', end='')
    #for x in op:
        #print('{:4.1f},'.format(x), end='')
    #print(']')
    #print('[', end='')
    #for x in bufin:
        #print('{:d},'.format(x), end='')
    #print(']')
    for idx, x in enumerate(bufin):
        if x != exp[idx]:
            print('FAIL')
            ok = False
            break
    if n_results != SIGLEN // 4:
        print('Siglen fail')
        ok = False
    return ok

for n, test in enumerate([test1, test2, test3, test4, test5, test6, test7, test8, test9]):
    if not test():
        print('Test', n +1, 'failed.')
        break
else:
    print('All tests passed OK.')
