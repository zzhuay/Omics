#!/bin/bash

########################################################################################################################
# mark PCR duplicates in BAM files
########################################################################################################################
for i in `cat samples.list`;do
{
	/software/gatk-4.1.7.0/gatk MarkDuplicates --REMOVE_DUPLICATES true -I $i.final.bam -O $i.final.md.bam -M $i.final.md.txt
}
done


########################################################################################################################
# Run SAVI2 to call mutations
########################################################################################################################
for i in `cat patients.list`;do
{
	/software/SAVI.sh $i\_blood.final.md.bam $i\_tumor.final.md.bam $i\_blood $i\_tumor $i\_SAVI
}
done


########################################################################################################################
# Run CNVKit to calculate copy number segmean
########################################################################################################################
for i in `cat patients.list`;do
{
	python /software/cnvkit/cnvkit.py batch $i\_tumor.final.md.bam --normal $i\_blood.final.md.bam -p 8 --targets ../ref/hs37d5/S07604514_Regions_NoChr.bed --antitargets ../ref/hs37d5/S07604514_anti_NoChr.bed --annotate ../ref/hs37d5/refFlat_NoChr.txt --fasta ../ref/hs37d5/hs37d5.fa --diagram --scatter --output-dir $i
	python /software/cnvkit/cnvkit.py export seg $i/$i\_tumor.final.call.cns -o $i/$i.final.call.seg
}
done