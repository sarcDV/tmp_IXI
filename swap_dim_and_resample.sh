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
	
	res1_=`echo $info_ | cut -d' ' -f14`
	res2_=`echo $info_ | cut -d' ' -f16`
	res3_=`echo $info_ | cut -d' ' -f18`
	res4_=`echo $info_ | cut -d' ' -f20`
	## swapdim 
	## fslswapdim IXI002-Guys-0828-T1.nii.gz z x y IXI002-Guys-0828-T1-axial.nii.gz 
    fslswapdim "$filename".nii.gz z x y "$filename"-axial.nii.gz 

	infob_=`fslinfo "$filename"-axial.nii.gz`
	
	res1b_=`echo $infob_ | cut -d' ' -f14`
	res2b_=`echo $infob_ | cut -d' ' -f16`
	res3b_=`echo $infob_ | cut -d' ' -f18`
	res4b_=`echo $infob_ | cut -d' ' -f20`


	div1_=`echo print "$res1b_"/"$res1_" | python2`
	div2_=`echo print "$res2b_"/"$res2_" | python2`
	div3_=`echo print "$res3b_"/"$res3_" | python2`

	## interpolate
	python3 $interpolation "$filename"-axial.nii.gz "$div1_" "$div2_" "$div3_"

	## 
	mv interpolated-*.nii.gz "$filename".nii.gz
	rm -rf "$filename"-axial.nii.gz
done

:<<COMMENT
fslinfo IXI002-Guys-0828-T1.nii.gz 
data_type	INT16
dim1		256
dim2		256
dim3		150
dim4		1
datatype	4
pixdim1		0.937500
pixdim2		0.937500
pixdim3		1.199997
pixdim4		0.000000
cal_max		0.000000
cal_min		0.000000
file_type	NIFTI-1+

fslinfo IXI002-Guys-0828-T1-axial.nii.gz 
data_type	INT16
dim1		150
dim2		256
dim3		256
dim4		1
datatype	4
pixdim1		1.199997  
pixdim2		0.937500
pixdim3		0.937500
pixdim4		0.000000
cal_max		0.000000
cal_min		0.000000
file_type	NIFTI-1+

COMMENT

