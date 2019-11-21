#!/usr/bin/env python3

import sys

def argparser():
        parser = argparse.ArgumentParser()
        parser.add_argument("--bin_size", required = True, help = "Size of insert size bins")
        parser.add_argument("--max_insert", required = True, help = "Max insert bin to use (every insert size larger than this goes in this bin)")
        args = parser.parse_args()
        return args

def find_duplicates():

    prev_read = [""] * 20
    insert_dict = {}

    for line in sys.stdin:
        line = line.strip().split("\t")
        insert_size = abs(int(line[8]))

        if insert_size not in insert_dict:
            insert_dict[insert_size] = [0, 0] # [all_reads, duplicates]
        insert_dict[insert_size][0] += 1

        if len(prev_read) != 20 and (int(line[1]) & 0x400 or int(prev_read[1]) & 0x400) and line[8] == prev_read[8] and line[3] == prev_read[3] and ("DT:Z:SQ" in prev_read[-1] or "DT:Z:SQ" in line[-1]):
            first_insert = abs(int(prev_read[8]))
            second_insert = abs(int(line[8]))

            if first_insert != second_insert:
                print(prev_read)
                print(line)
                raise "These duplicates don't have the same insert sizes, are you sure the bam is sorted?"
            insert_dict[insert_size][1] += 1

        prev_read = line
    return insert_dict

def make_bins(insert_dict, bin_size, max_insert):

    bin_dict = {x:[0, 0] for x in range(0, max_insert + 1, bin_size)}
    for insert_size in insert_dict:
        if insert_size >= max_insert:
            bin = max_insert
        else:
            bin = bin_size * int(insert_size / bin_size)

        bin_dict[bin][0] += insert_dict[insert_size][0]
        bin_dict[bin][1] += insert_dict[insert_size][1]
    
    return bin_dict


if __name__ == "__main__":
    args = argparser()
    insert_dict = find_duplicates()
    bin_dict = make_bins(insert_dict, args.bin_size, args.max_insert)

    for bin in sorted(bin_dict.keys(), key=int):
        print("{}\t{}\t{}\t{}\t{}".format(sys.argv[1], bin, bin_dict[bin][1], bin_dict[bin][0], bin_dict[bin][1] / bin_dict[bin][0]))
