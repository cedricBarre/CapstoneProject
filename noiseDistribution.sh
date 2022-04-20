#!/bin/bash
module load minc-toolkit

reference_image="$1" #input
minc_files_path = "$2"
output_path="$3" #output
upper_threshold = 19 


# Transform each nifti file and create 
scan_name="$(basename -- $reference_image)" # Extract basename
scan_name="${scan_name%%.*}" # Remove nifti extension
minc_file="$original_file.mnc" # Remove nifti extension
nii2mnc -noscanrange $reference_image ./$minc_files_path/$minc_file

mincmath -segment -const2 0 upper_threshold original_file.mnc binarized_file.mnc
mincmorph -erosion binarized_file.mnc binarized_eroded_file.mnc


mnc2nii $output_path/binarized_eroded_file.mnc $output_path/binarized_eroded_file.nii
   gzip $output_path/binarized_eroded_file.nii
   output_file="$output_path/binarized_eroded_file.mnc"





