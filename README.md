# Fast Filters for the Pyboard

V0.91 22nd March 2018  
Author: Peter Hinch

# Introduction

This repository contains code for targets running MicroPython and supporting
the ARM Thumb assembly language, in particular the Pyboard.

There are two libraries, both written using the inline assembler for
performance.

`fir.py` This, described below, is intended for real time filtering of incoming
analog data using FIR (finite impulse response) filtering.

`filt.py` (in the non_realtime directory). This is intended for processing of
sample sets acquired by `ADC.read_timed()`, and is described [here](./non_realtime/FILT.md).
The algorithm can be configured for continuous (circular buffer) or
discontinuous sample sets. It can optionally perform decimation. In addition to
FIR filtering it can be employed for related functions such as convolution,
cross- and auto-correlation.

# fir.py

These filters are intended to process integer data arriving in real time from a
transducer and are capable of being used in interrupt handlers. If you're new
to this, see the last section of this readme.

Two filters are currently supported: a simple moving average and an FIR filter.
Code is written in ARM Thumb assembler for performance. They operate on 32 bit
signed integers. On the MicroPython board the moving average takes 8uS and the
FIR takes 15uS for a typical set of coefficients. FIR filters can be designed
for low pass, high pass, bandpass or band stop applications and the site
[TFilter](http://t-filter.engineerjs.com/) enables these to be computed.

## Demo program

The file lpf.py uses the board as a low pass filter with a cutoff of 40Hz. It
processes an analog input presented on pin X7, filters it, and outputs the
result on DAC2 (X6). For convenience the code includes a swept frequency
oscillator with output on DAC1 (X5). By linking X5 and X7 the filtered result
can be viewed on X6.

The filter uses Timer 4 to sample the incoming data at 2KHz.
The program generates a swept frequency sine wave on DAC1 and reads it using
the ADC on pin X7. The filtered signal is output on DAC2. The incoming signal
is sampled at 2KHz by means of Timer 4, with the FIR filter operating in the
timer's callback handler.

When using the oscillator to test filters you may see occasional transients
occurring in the stopband. These are a consequence of transient frequency
components caused by the step changes in the oscillator frequency: this can be
demonstrated by increasing the delay between frequency changes. Ideally the
oscillator would issue a slow, continuous sweep.

firtest.py illustrates the FIR operation and computes execution times with
different sets of coefficients.

## Performance

A 41 tap FIR on a MicroPython board takes 16uS. For other sizes the time can be
estimated as 10 + 0.136N uS where N is number of coefficients. The penalty in
terms of memory use is that each coefficient requires 8 bytes in the two arrays
used by the code.

## fir.py Usage

The fir.fir() function takes three arguments:
 1. An integer array of length equal to the number of coeffcients + 3.
 2. An integer array of coefficients.
 3. The new data value.
 
The function returns an integer which is the current filtered value.  
The array must be initialised as follows:
 1. data[0] should be set to len(data)
 2. data[1] is a scaling value in range 0..31: see scaling below.
 3. Other elements of the data array must be zero.
 
The website cited above generates symmetrical (linear phase) sets of
coefficients. In other words, for a set of n coefficients,
`coeff[x] == coeff[n-x]`. For coefficient arrays lacking this symmetry note
that the code applies coefficients to samples such that the oldest sample is
multiplied by coeff[0] and so on with the newest getting coeff[n].

## avg.py Moving Average Usage

avg.avg() takes two arguments:
 1. An integer array of length equal to the no. of entries to average over +3.
 2. The new data value.

The function returns an integer which is the current filtered value.  
Initially all elements of the data array must be zero, except data[0] which
should be set to `len(data)`  
The program `avgtest.py` illustrates its operation.

## Scaling

Calculations are based on 32 bit signed arithmetic. Given that few transducers
offer more than 16 bit precision there is a lot of headroom. Nevertheless
overflow can occur depending on the coefficient size. The maximum output from
the multiplication is max(data)*max(coeffs) but the subsequent addition offers
further scope for overflow. In applications with analog output there is little
point in creating results with more precision than the output DAC. The `fir()`
function includes scaling by performing an arithmetic right shift on the result
of each multiplication. This can be in the range of 0-31 bits, although 20 bits
is a typical maximum.  
Doubtless there is an analytical way to determine the optimum scaling. Alas I
don't know it. In my `lpf.py` example I apply a scaling of 16 bits to preserve
the 12 bit resolution of the ADC then scale the result in Python to match the
DAC.

## FIR Coefficients


I have provided a utility coeff_format.py to simplify the conversion of
coefficients into Python code. Use the website cited above and set it to
provide integer coefficient. Cut and paste the list of coefficients into a
file: this will have one integer per line. Then run  
`python3 coeff_format.py inputfilename outputfilename.py`  
The result will be a Python file defining the array.

# Absolute Beginners

Data arriving from transducers often needs to be filtered to render it useful.
Reasons include reducing noise (random perturbations) in the data, isolating a
particular signal or shaping the response to sudden changes in the data value.
A common approach to reducing noise is to take a moving average of the last N
samples. While this is computationally simple and hence fast, it is a
relatively crude form of filtering because the oldest sample in the set has the
same weight as the most recent. This is often non-optimal.

FIR (finite impulse response) filters can be viewed as an extension of the
moving average concept where each sample is allocated a different weight
depending on its age. These weights are defined by a set of coefficients. The
result is calculated by multiplying each sample by its coefficient before
adding them; a moving average corresponds to the situation where all
coefficients are set to 1. By adjusting the coefficients you can alter the
relative weights of the data values, with the most recent having a different
weight to the next most recent, and so on.

In practice FIR filters can be designed to produce a range of filter types:
low pass, high pass, bandpass, band stop and so on. They can also be tailored
to produce a specific response to sudden changes (impulse response). The
process of computing the coefficients is complex, but the link above provides a
simple GUI approach. Set the application to produce 16 or 32 bit integer
values, set your desired characteristics and press "Design Filter". Then
proceed as suggested above to convert the results to Python code.
