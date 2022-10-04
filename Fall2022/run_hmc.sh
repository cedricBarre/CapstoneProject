#!/bin/bash

POSITIONAL_ARGS=()
INPUT=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--input)
      INPUT="$2"
      shift # past argument
      shift # past value
      ;;
    -o|--output)
      OUTPUT="$2"
      shift # past argument
      shift # past value
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

if [ "$INPUT" == "" ]; then
    echo Failed to provide an input folder
    exit 1
fi
if [ "$OUTPUT" == "" ]; then
    echo Failed to provide an output folder
    exit 1
fi

singularity exec --bind ./HMC_isolated.py:/mnt/HMC_isolated.py \
                 --bind $INPUT:/mnt/input \
                 --bind $OUTPUT:/mnt/output \
                 ../../Fall2022/rabies.sif \
                 python /mnt/HMC_isolated.py /mnt/input /mnt/output 

#singularity exec --bind ./:/mnt/ ../../Fall2022/rabies.sif antsMotionCorr --help