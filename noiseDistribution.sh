module load minc-toolkit
minc_scan=$1 #input
output_path=$2 #output
#Using the mincmath
mincmath -segment -const2 0 19 $minc_scan $output_path/binarized_file.mnc
#First Erosion
mincmorph -erosion ./binarized_file.mnc ./binarized_eroded_file01.mnc
#Transforming the minc file in nifti of the first erosion
mnc2nii $output_path/binarized_eroded_file01.mnc $output_path/binarized_eroded_file01.nii
gzip $output_path/binarized_eroded_file01.nii
#Second Erosion
mincmorph -erosion $output_path/binarized_eroded_file01.mnc $output_path/binarized_eroded_file02.mnc
#Transforming the minc file in nifti of the second erosion
mnc2nii $output_path/binarized_eroded_file02.mnc $output_path/binarized_eroded_file02.nii
gzip $output_path/binarized_eroded_file02.nii
#Thrid erosion
mincmorph -erosion $output_path/binarized_eroded_file02.mnc $output_path/binarized_eroded_file03.mnc
#Transforming the minc file in nifti of the third erosion
mnc2nii $output_path/binarized_eroded_file03.mnc $output_path/binarized_eroded_file03.nii
gzip $output_path/binarized_eroded_file03.nii
#Fourth Erosion
mincmorph -erosion $output_path/binarized_eroded_file03.mnc $output_path/binarized_eroded_file04.mnc
#Transforming the minc file in nifti of the fourth erosion
mnc2nii $output_path/binarized_eroded_file04.mnc $output_path/binarized_eroded_file04.nii
gzip $output_path/binarized_eroded_file04.nii
#Fift Erosion
mincmorph -erosion $output_path/binarized_eroded_file04.mnc $output_path/binarized_eroded_file05.mnc
#Transforming the minc file in nifti of the fourth erosion
mnc2nii $output_path/binarized_eroded_file05.mnc $output_path/binarized_eroded_file05.nii
gzip $output_path/binarized_eroded_file05.nii
for file in /data/scratch/jed/noise_distribution/*
do echo "\r files: ${file##*/}"
done