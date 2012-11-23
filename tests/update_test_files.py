#! /usr/bin/python
import sys
import examples

for filename in sys.argv[1:]:
    examples.save_output(filename)

