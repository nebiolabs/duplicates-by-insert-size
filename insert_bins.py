#!/usr/bin/env python3

import sys
import argparse

def argparser():
        parser = argparse.ArgumentParser()
        parser.add_argument("--bin_size", required = True, help = "Size of insert size bins")
        parser.add_argument("--max_insert", required = True, help = "Max insert bin to use (every insert size larger than this goes in this bin)")
        parser.add_argument("--library", required = True, help = "Library name (will be the first column in the output)")
        args = parser.parse_args()
        return args

def find_duplicates():
    """ Finds all reads with the 0x400 flag set by Picard MarkDuplicates """

    insert_dict = {}

    read_num = 0
    for line in sys.stdin:

        if line.startswith("@"):
            continue # Skip header lines, if present
        read_num += 1
        if read_num % 1000000 == 0:
            print("Processed {} reads\r".format(read_num), file=sys.stderr, end = "")
        line = line.strip().split("\t")
        insert_size = abs(int(line[8]))

        if insert_size not in insert_dict:
            insert_dict[insert_size] = [0, 0, 0] # [all_reads, optical duplicates, pcr duplicates]
        insert_dict[insert_size][0] += 1

        if int(line[1]) & 0x400:
            if "DT:Z:SQ" in line:
                dup_type = 1 # The index for optical duplicates
            elif "DT:Z:LB" in line:
                dup_type = 2 # The index for pcr duplicates
            else:
                print(line)
                raise Exception("This read is marked as a duplicate, but doesn't have a 'DT:Z:<>' flag set. Make sure you ran Picard's markduplicates with '--TAGGING_POLICY All' set.")

            insert_dict[insert_size][dup_type] += 1

    return insert_dict

def make_bins(insert_dict, bin_size, max_insert):
    """ Assigns the insert sizes and corresponding duplicates to bins of <bin size> size"""

    bin_dict = {x:[0, 0, 0] for x in range(0, max_insert + 1, bin_size)}
    for insert_size in insert_dict:
        if insert_size >= max_insert:
            bin = max_insert
        else:
            bin = bin_size * int(insert_size / bin_size)

        for x in range(0, 3):
            bin_dict[bin][x] += insert_dict[insert_size][x]
    
    return bin_dict

def run_script():
    args = argparser()
    if int(args.bin_size) > int(args.max_insert):
        raise Exception("Max insert size needs to be >= bin size")

    insert_dict = find_duplicates()
    bin_dict = make_bins(insert_dict, int(args.bin_size), int(args.max_insert))

    print("Library\tBin\tTotal reads\tOptical duplicates\tPCR duplicates\tOptical duplicate rate\tPCR duplicate rate\tTotal duplicate rate")
    for bin in sorted(bin_dict.keys(), key=int):
        if bin_dict[bin][0] == 0: # To avoid dividing by zero if any bins have no reads
            bin_dict[bin].extend([0,0,0])
        else:
            bin_dict[bin].append(bin_dict[bin][1] / bin_dict[bin][0]) # Optical duplicate rate
            bin_dict[bin].append(bin_dict[bin][2] / bin_dict[bin][0]) # PCR duplicate rate
            bin_dict[bin].append((bin_dict[bin][1] + bin_dict[bin][2]) / bin_dict[bin][0]) # Total duplicate rate

        print("{}\t{}\t{}".format(args.library, bin, "\t".join(map(str, bin_dict[bin]))))

if __name__ == "__main__":
    run_script()