#!/bin/bash

POSITIONAL_ARGS=()
MOVING=""
OUTPUT=""
REFERENCE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -m|--moving)
      MOVING="$2"
      shift # past argument
      shift # past value
      ;;
    -o|--output)
      OUTPUT="$2"
      shift # past argument
      shift # past value
      ;;
    -r|--reference)
      REFERENCE="$2"
      shift # past argument
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

if [ "$MOVING" == "" ]; then
    echo Failed to provide a moving image
    exit 1
fi
if [ "$OUTPUT" == "" ]; then
    echo Failed to provide an output folder
    exit 1
fi
if [ "$REFERENCE" == "" ]; then
    echo Failed to provide a reference image
    exit 1
fi

singularity exec --bind ./HMC_isolated.py:/mnt/HMC_isolated.py \
                 --bind $MOVING:/mnt/moving.nii.gz \
                 --bind $REFERENCE:/mnt/reference.nii.gz \
                 --bind $OUTPUT:/mnt/output \
                 ../../Fall2022/rabies.sif \
                 python /mnt/HMC_isolated.py /mnt/moving.nii.gz /mnt/reference.nii.gz /mnt/output 

#singularity exec --bind ./:/mnt/ ../../Fall2022/rabies.sif antsMotionCorr --help