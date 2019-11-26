# optical-duplicate-insert-size
Calculates the optical duplicate rate per insert size bins

Usage:
```
samtools view <duplicate marked sam/bam file> | insert_bins.py --bin_size <size of insert bins> --max_insert <Max insert size> --library <Library name (first column in output file)>
```

Alternatively, the data can be piped in with 'cat' if it's a sam file.

This program finds all reads marked as duplicate by Picard MarkDuplicates, and assigns them as either an optical duplicate or PCR duplicate (based on the DT:Z:\<SQ/LB> flag set by MarkDuplicates. To get this flag, you'll have to run MarkDuplicates with the --TAGGING_POLICY=All option set.
