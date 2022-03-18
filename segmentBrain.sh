#!/bin/bash
module load ANTs
module load minc-toolkit

# Load atlases, masks and labels
atlas_for_reg="${QUARANTINE_PATH}/resources/Dorr_2008_Steadman_2013_Ullmann_2013_Richards_2011_Qiu_2016_Egan_2015_40micron/100um/DSURQE.mnc"
atlas_mask="${QUARANTINE_PATH}/resources/Dorr_2008_Steadman_2013_Ullmann_2013_Richards_2011_Qiu_2016_Egan_2015_40micron/100um/DSURQE_mask.mnc"

# Mask for the full brain
atlas_full_mask="/data/chamal/projects/mila/2019_MTR_on_Cryoprobe/resources_tissue_labels/DSURQE_100micron_mask.mnc"

mask_reference_file_path="$1"
minc_files_path="$2"
output_path="$3"

mkdir -p $output_path/transforms_from_subject_to_atlas
mkdir -p $output_path/n4_bias_corrected
mkdir -p $output_path/masks

# Transform each nifti file and create the masks
scan_name="$(basename -- $mask_reference_file_path)" # Extract basename
scan_name="${scan_name%%.*}" # Remove nifti extension
minc_file="$scan_name.mnc" # Remove nifti extension
nii2mnc -noscanrange $mask_reference_file_path ./$minc_files_path/$minc_file

./mouse-preprocessing-N4corr.sh $output_path/minc_files/$minc_file $output_path/n4_bias_corrected/"$scan_name"_N4corr.mnc

./antsRegistration_affine_SyN.sh $output_path/n4_bias_corrected/"$scan_name"_N4corr.mnc $atlas_for_reg $atlas_mask $output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas

antsApplyTransforms -d 3 -i $atlas_mask \
   -t [$output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas_output_0_GenericAffine.xfm,1] \
   -t $output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas_output_1_inverse_NL.xfm -n GenericLabel \
   -o $output_path/masks/PDw_mask.mnc --verbose \
	 -r $output_path/n4_bias_corrected/"$scan_name"_N4corr.mnc

mnc2nii $output_path/masks/PDw_mask.mnc $output_path/masks/PDw_mask.nii
gzip $output_path/masks/PDw_mask.nii
