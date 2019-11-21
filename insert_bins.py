#!/usr/bin/env python3

import sys
# import math
# import matplotlib.pyplot as plt

prev_read = [""] * 20
bin_dict = {}
for line in sys.stdin:
    line = line.strip().split("\t")
    insert_size = line[8].strip("-")
    if len(insert_size) < 3:
        bin = "0"
    else:
        bin = insert_size[:-2]
    if int(bin) > 10:
        bin = "11"
    # print(insert_size, bin)
    if bin not in bin_dict:
        bin_dict[bin] = [0, 0] # [all_reads, duplicates]
    bin_dict[bin][0] += 1
    if len(prev_read) != 20 and (int(line[1]) & 0x400 or int(prev_read[1]) & 0x400) and line[8] == prev_read[8] and line[3] == prev_read[3] and ("DT:Z:SQ" in prev_read[-1] or "DT:Z:SQ" in line[-1]):
        first_insert = prev_read[8].strip("-")
        second_insert = line[8].strip("-")
        # print(prev_read)
        # print(line)
        # print(first_insert, second_insert)
        # print("\n")
        if first_insert != second_insert:
            print(prev_read)
            print(line)
            raise ":("
        bin_dict[bin][1] += 1

    prev_read = line

for bin in sorted(bin_dict.keys(), key=int):
    print("{}\t{}\t{}\t{}\t{}".format(sys.argv[1], bin, bin_dict[bin][1], bin_dict[bin][0], bin_dict[bin][1] / bin_dict[bin][0]))
