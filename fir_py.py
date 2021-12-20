# fir_py.py FIR filter implemented with Viper
# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from array import array
# Closures under Viper, see
# https://github.com/micropython/micropython/issues/8086
# The workround seems fragile so I'm using an array to hold state
def create_fir(coeffs, shift):
    nc = len(coeffs)
    data = array('i', (0 for _ in range(nc)))
    ctrl = array('i', (0, shift, nc))
    @micropython.viper
    def inner(val : int) -> int:
        buf = ptr32(data)
        ctl = ptr32(ctrl)
        co = ptr32(coeffs)
        shift : int = ctl[1]
        nc : int = ctl[2]
        end : int = nc - 1
        i : int = ctl[0]
        buf[i] = val
        i = (i + 1) if (i < end) else 0
        ctl[0] = i
        res : int = 0
        for x in range(nc):
            res += (co[x] * buf[i]) >> shift
            i = (i + 1) if (i < end) else 0
        return res
    return inner
