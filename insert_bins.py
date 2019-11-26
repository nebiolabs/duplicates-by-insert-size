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

    prev_read = [""] * 20
    insert_dict = {}

    for line in sys.stdin:

        if line.startswith("@"):
            continue
        line = line.strip().split("\t")
        insert_size = abs(int(line[8]))

        if insert_size not in insert_dict:
            insert_dict[insert_size] = [0, 0, 0] # [all_reads, optical duplicates, pcr duplicates]
        insert_dict[insert_size][0] += 1

        if len(prev_read) != 20 and (int(line[1]) & 0x400 or int(prev_read[1]) & 0x400) and line[8] == prev_read[8] and line[3] == prev_read[3]:
            if ("DT:Z:SQ" in prev_read or "DT:Z:SQ" in line):
                dup_type = 1 # The index for optical duplicates
            elif ("DT:Z:LB" in prev_read or "DT:Z:LB" in line):
                dup_type = 2 # The index for pcr duplicates
            else:
                print(prev_read)
                print(line)
                raise Exception("These reads are marked as duplicates, but don't have a 'DT:Z:<>' flag set. Make sure you ran Picard's markduplicates with '--TAGGING_POLICY All' set.")

            first_insert = abs(int(prev_read[8]))
            second_insert = abs(int(line[8]))

            if first_insert != second_insert:
                print(prev_read)
                print(line)
                raise Exception("These duplicates don't have the same insert sizes, are you sure the bam is sorted?")
            insert_dict[insert_size][dup_type] += 1

        prev_read = line
    return insert_dict

def make_bins(insert_dict, bin_size, max_insert):

    bin_dict = {x:[0, 0, 0] for x in range(0, max_insert + 1, bin_size)}
    for insert_size in insert_dict:
        if insert_size >= max_insert:
            bin = max_insert
        else:
            bin = bin_size * int(insert_size / bin_size)

        bin_dict[bin][0] += insert_dict[insert_size][0]
        bin_dict[bin][1] += insert_dict[insert_size][1]
        bin_dict[bin][2] += insert_dict[insert_size][2]
    
    return bin_dict


if __name__ == "__main__":
    args = argparser()
    insert_dict = find_duplicates()
    bin_dict = make_bins(insert_dict, int(args.bin_size), int(args.max_insert))

    print("Library\tBin\tTotal reads\tOptical duplicates\tPCR duplicates\tOptical duplicate rate\tPCR duplicate rate\tTotal duplicate rate")
    for bin in sorted(bin_dict.keys(), key=int):
        if bin_dict[bin][0] == 0:
            bin_dict[bin].extend([0,0,0])
        else:
            bin_dict[bin].append(bin_dict[bin][1] / bin_dict[bin][0])
            bin_dict[bin].append(bin_dict[bin][2] / bin_dict[bin][0])
            bin_dict[bin].append((bin_dict[bin][1] + bin_dict[bin][2]) / bin_dict[bin][0])

        print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(args.library, bin, bin_dict[bin][0], bin_dict[bin][1], bin_dict[bin][2], \
                                                      bin_dict[bin][3], bin_dict[bin][4], bin_dict[bin][5]))