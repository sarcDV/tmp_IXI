#!/bin/bash
cd T1b/

N=8
(for file in *.nii.gz;
do
	((i=i%N)); ((i++==0)) && wait
	(new_name_=$(echo "$file" | cut -f 1 -d '.') 
	echo  " ... brain extraction / skull stripping ... ""$new_name_" 
	bet2 "$new_name_".nii.gz ../T1brain/"$new_name_"_brain ) &
	
done
)