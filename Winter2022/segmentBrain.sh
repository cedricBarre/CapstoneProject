#!/bin/bash
module load ANTs
module load minc-toolkit

BOLD='\033[1;'
NORMAL='\033[0m'
BOLD_YELLOW='\033[1;33m'

# Load atlases, masks and labels
atlas_for_reg="${QUARANTINE_PATH}/resources/Dorr_2008_Steadman_2013_Ullmann_2013_Richards_2011_Qiu_2016_Egan_2015_40micron/100um/DSURQE.mnc"
atlas_mask="${QUARANTINE_PATH}/resources/Dorr_2008_Steadman_2013_Ullmann_2013_Richards_2011_Qiu_2016_Egan_2015_40micron/100um/DSURQE_mask.mnc"

# Mask for the full brain
atlas_full_mask="/data/chamal/projects/mila/2019_MTR_on_Cryoprobe/resources_tissue_labels/DSURQE_100micron_mask.mnc"

mask_reference_file_path="$1"
minc_files_path="$2"
output_path="$3"
mask_file="$4"

if [ -z $mask_file ]; then 

   echo -e "${BOLD_YELLOW}Starting mask creation process...${NORMAL}"

   # Transform each nifti file and create the masks
   scan_name="$(basename -- $mask_reference_file_path)" # Extract basename
   scan_name="${scan_name%%.*}" # Remove nifti extension
   minc_file="$scan_name.mnc" # Remove nifti extension
   nii2mnc -noscanrange $mask_reference_file_path ./$minc_files_path/$minc_file

   echo -e "${BOLD}/ Bias field correction -------------- /${NORMAL}"
   ./mouse-preprocessing-N4corr.sh $output_path/minc_files/$minc_file $output_path/n4_bias_corrected/"$scan_name"_N4corr.mnc

   echo -e "${BOLD}/ Registration${NORMAL}"
   ./antsRegistration_affine_SyN.sh $output_path/n4_bias_corrected/"$scan_name"_N4corr.mnc $atlas_for_reg $atlas_mask $output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas

   echo -e "${BOLD}/ Mask creation -------------- /${NORMAL}"
   antsApplyTransforms -d 3 -i $atlas_mask \
      -t [$output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas_output_0_GenericAffine.xfm,1] \
      -t $output_path/transforms_from_subject_to_atlas/$scan_name-registered_to_atlas_output_1_inverse_NL.xfm -n GenericLabel \
      -o $output_path/masks/PDw_mask.mnc --verbose \
      -r $output_path/n4_bias_corrected/"$scan_name"_N4corr.mnc

   echo -e "${BOLD}/ Exporting mask -------------- /${NORMAL}"
   mnc2nii $output_path/masks/PDw_mask.mnc $output_path/masks/PDw_mask.nii
   gzip $output_path/masks/PDw_mask.nii

   mask_file="$output_path/masks/PDw_mask.mnc"
fi

echo -e "${BOLD_YELLOW}Changing mask file format...${NORMAL}"
# Make sure the mask has .mnc extension
if [ "${mask_file##*.}" != "mnc" ] ; then
   new_mask_file="${mask_file%%.*}".mnc
   nii2mnc -noscanrange $mask_file $new_mask_file
   mask_file=$new_mask_file
fi

echo -e "${BOLD_YELLOW}Denoising each scan...${NORMAL}"
# Apply denoising on every scan in every directory
for sorted_dir in $output_path/nifti_files/*/ ; do
   for nifti_file in $(find ./$sorted_dir -type f -name "*.nii.gz")
   do
      rg_value="$(basename $sorted_dir)"
      scan_name="$(basename -- $nifti_file)" # Extract basename
      scan_name="${scan_name%%.*}" # Remove nifti extension
      minc_file="$scan_name.mnc" # Remove nifti extension
      nii2mnc -noscanrange $nifti_file ./$minc_files_path/$rg_value/$minc_file

      DenoiseImage -d 3 -i $minc_files_path/$rg_value/$minc_file -n Rician -x $mask_file --verbose -o $output_path/minc_files/$rg_value/denoised_$minc_file

      mnc2nii $output_path/minc_files/$rg_value/denoised_$minc_file $output_path/denoised/$rg_value/$scan_name.nii
      gzip $output_path/denoised/$rg_value/$scan_name.nii
   done
done
