# duplicates-by-insert-size
This program finds all reads marked as duplicate by Picard MarkDuplicates, and assigns them as either an optical duplicate or PCR duplicate (based on the DT:Z:\<SQ/LB> flag set by MarkDuplicates. To get this flag, you'll have to run MarkDuplicates with the --TAGGING_POLICY=All option set.

Usage:
```
samtools view <duplicate marked sam/bam file> | insert_bins.py --bin_size <size of insert bins> --max_insert <Max insert size> --library <Library name (first column in output file)>
```

Alternatively, the data can be piped in with 'cat' if it's a sam file. One could also pipe the input straight from Picard MarkDuplicates (via /dev/stdout), but the data would not be saved, so it wouldn't be helpful if you wanted to use the duplicate-marked data for other purposes.


Prints to stdout the following columns:

Library | Bin | Total reads | Optical duplicates | PCR duplicates | Optical duplicate rate | PCR duplicate rate | Total duplicate rate

As an example, pcr-free libraries might look something like the below image, with a very low overall PCR duplicate rate and relatively higher optical duplicate rate:
![pcr-free example](/images/pcr-free.png)



On the other extreme, targeted libraries might have the reverse pattern (unless using UMIs), in which there is a very high called PCR duplicate rate and relatively low optical duplicate rate:
![targeted example](/images/targeted_capture.png)
