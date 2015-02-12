# Utility to convert a set of FIR coefficients into Python code.
# Cut and paste the (16 bit integer) coeffs from
# http://t-filter.appspot.com/fir/index.html into a file. This will
# have one coefficient per line.
# This will create a readable output Python file defining the array.

# Author: Peter Hinch 10th Feb 2015
import sys

def r(infile, outfile):
    with open(infile, "r") as f:
        with open(outfile, "w") as g:
            st = "import array\ncoeffs = array.array('i', ("
            g.write(st)
            x = 0
            st = ""
            while st == "":
                st = f.readline().strip() # ignore leading whitespace
            starting = True
            while st != "":
                if starting:
                    starting = False
                else:
                    g.write(",")
                x += 1
                g.write(st)
                if x % 15 == 0:
                    g.write("\n  ")
                st = f.readline().strip()
            g.write("))\n\n")

def main():
    if len(sys.argv) != 3 or sys.argv[0] == "--help":
        print("Usage: python3 coeff_format.py data_filename python_filename")
    else:
        r(sys.argv[1], sys.argv[2])

main()

