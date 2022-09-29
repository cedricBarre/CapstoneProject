module load minc-toolkit
minc_scan=$1 #input
output_path=$2 #output
#Using the mincmath
mincmath -segment -const2 0 4000000 $minc_scan ./binarized_file.mnc
mnc2nii ./binarized_file.mnc ./binarized_file.nii
gzip ./binarized_file.nii
#First Erosion
mincmorph -erosion ./binarized_file.mnc ./binarized_eroded_file01.mnc
#Transforming the minc file in nifti of the first erosion
mnc2nii ./binarized_eroded_file01.mnc ./binarized_eroded_file01.nii
gzip ./binarized_eroded_file01.nii
#Second Erosion
mincmorph -erosion ./binarized_eroded_file01.mnc ./binarized_eroded_file02.mnc
#Transforming the minc file in nifti of the second erosion
mnc2nii ./binarized_eroded_file02.mnc ./binarized_eroded_file02.nii
gzip ./binarized_eroded_file02.nii
#Thrid erosion
mincmorph -erosion ./binarized_eroded_file02.mnc ./binarized_eroded_file03.mnc
#Transforming the minc file in nifti of the third erosion
mnc2nii ./binarized_eroded_file03.mnc ./binarized_eroded_file03.nii
gzip ./binarized_eroded_file03.nii
#Fourth Erosion
mincmorph -erosion ./binarized_eroded_file03.mnc ./binarized_eroded_file04.mnc
#Transforming the minc file in nifti of the fourth erosion
mnc2nii ./binarized_eroded_file04.mnc ./binarized_eroded_file04.nii
gzip ./binarized_eroded_file04.nii
#Fift Erosion
mincmorph -erosion ./binarized_eroded_file04.mnc ./binarized_eroded_file05.mnc
#Transforming the minc file in nifti of the fourth erosion
mnc2nii ./binarized_eroded_file05.mnc ./binarized_eroded_file05.nii
gzip ./binarized_eroded_file05.nii
for file in /data/scratch/jed/noise_distribution/*
do echo "\r files: ${file##*/}"
done