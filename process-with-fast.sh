#!/bin/bash
cd T1brain/

N=8
(for file in *.nii.gz;
do
	((i=i%N)); ((i++==0)) && wait
	(filename=$(basename -- "$file")
	extension="${filename##*.}"
	filename="${filename%.*.*}"

	echo "... processing ..." "$filename" 
	fast "$filename".nii.gz 
	rm -rf "$filename"_mixeltype.nii.gz "$filename"_pve*.nii.gz) &
	## threshold 5%:
	## fslmaths "$new_name_".nii.gz -thrp 5 "$new_name_"_mask.nii.gz 
	## binarize, create mask:
	## fslmaths "$new_name_"_mask.nii.gz  -bin "$new_name_"_mask.nii.gz
done
)

mv *_seg.nii.gz ../T1seg/