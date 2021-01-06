#!/bash/bin
interpolation="/media/alex/Data_Alex/tmp_IXI/fft_interpolation_resample.py"
cd T1/
for files in *;
do
	# echo "$files"
	filename=$(basename -- "$files")
	extension="${filename##*.}"
	filename="${filename%.*.*}"

	echo "... processing ..." "$filename"

	info_=`fslinfo "$filename".nii.gz`
	dim1_=`echo $info_ | cut -d' ' -f4`
	dim2_=`echo $info_ | cut -d' ' -f6`
	dim3_=`echo $info_ | cut -d' ' -f8`
	dim4_=`echo $info_ | cut -d' ' -f10`
	
	res1_=`echo $info_ | cut -d' ' -f14`
	res2_=`echo $info_ | cut -d' ' -f16`
	res3_=`echo $info_ | cut -d' ' -f18`
	res4_=`echo $info_ | cut -d' ' -f20`

	# echo "$dim1_" "$dim2_" "$dim3_"
	fslroi "$filename".nii.gz "$filename".nii.gz 1 "$dim1_" 1 "$dim2_" 1 180

done