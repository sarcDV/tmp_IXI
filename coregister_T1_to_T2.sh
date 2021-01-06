#!/bin/bash
cd T1/

N=8
(for files in *;
do
	# echo "$files"
	((i=i%N)); ((i++==0)) && wait
	(filename=$(basename -- "$files")
	extension="${filename##*.}"
	filename="${filename%-T1.*.*}"

	echo "... processing ..." "$filename"
	fslswapdim "$filename"-T1.nii.gz x -y z "$filename"-T1-tmp.nii.gz
	flirt -in "$filename"-T1-tmp.nii.gz -ref ../T2/"$filename"-T2.nii.gz -out ../T1b/"$filename"-T1.nii.gz 
	rm -rf "$filename"-T1-tmp.nii.gz) &

done
)