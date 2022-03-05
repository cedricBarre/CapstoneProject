#!/bin/bash
module load ANTs
module load minc-toolkit

# Load atlases, masks and labels
atlas_for_reg="${QUARANTINE_PATH}/resources/Dorr_2008_Steadman_2013_Ullmann_2013_Richards_2011_Qiu_2016_Egan_2015_40micron/100um/DSURQE.mnc"
atlas_mask="${QUARANTINE_PATH}/resources/Dorr_2008_Steadman_2013_Ullmann_2013_Richards_2011_Qiu_2016_Egan_2015_40micron/100um/DSURQE_mask.mn"

# Mask for the full brain
atlas_full_mask="/data/chamal/projects/mila/2019_MTR_on_Cryoprobe/resources_tissue_labels/DSURQE_100micron_mask.mnc"

nifti_files_path="$1"
minc_files_path="$2"
output_path="$3"

mkdir -p $output_path/transforms_from_subject_to_atlas
mkdir -p $output_path/masks

# Transform each nifti file and create the masks
for nifti_file in $(find ./$nifti_files_path -type f -name "*.nii.gz")
do
    scan_name="$(basename -- $nifti_file)" # Extract basename
    scan_name="${scan_name%%.*}" # Remove nifti extension
    minc_file="$scan_name.mnc" # Remove nifti extension
    mask_nifti_file="$scan_name-mask.nii.gz"
    nii2mnc -noscanrange $nifti_file ./$minc_files_path/$minc_file

    ./antsRegistration_affine_SyN.sh $minc_file $atlas_for_req $atlas_mask $output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas

    antsApplyTransforms -d 3 -i $atlas_mask \
        -t [$output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas_output_0_GenericAffine.xfm,1] \
        -t $output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas_output_1_inverse_NL.xfm -n GenericLabel \
        -o $output_path/masks/$scan_name-mask.mnc --verbose \ 
	    -r ./$minc_files_path/$minc_file
    
    #register $output_path/masks/$scan_name-mask.mnc ./$minc_files_path/$minc_file

    mnc2nii -noscanrange $output_path/masks/$scan_name-mask.mnc $nifti_files_path/$scan_name-mask.nii.gz
done