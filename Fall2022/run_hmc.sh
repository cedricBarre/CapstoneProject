#!/bin/bash

POSITIONAL_ARGS=()
INPUT=""
OUTPUT=""
DATASET=""
LATEST_ANTS=""
HELP=0
SINGULARITY=0

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
    -d|--dataset)
      DATASET="-d"
      shift # past argument
      ;;
    -l|--latest_ants)
      LATEST_ANTS="-l"
      shift # past argument
      ;;
    -s|--singularity)
      SINGULARITY=1
      shift # past argument
      ;;
    -h|--help)
      HELP=1
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

if [ $HELP == 1 ]; then
  if [ $SINGULARITY == 1 ]; then 
      singularity exec --bind ./HMC_isolated.py:/mnt/HMC_isolated.py \
                      ../../Fall2022/rabies.sif \
                      python /mnt/HMC_isolated.py -h
  else
      python ./HMC_isolated.py -h
  fi
  exit 0
fi

if [ "$INPUT" == "" ]; then
    echo Failed to provide an input folder
    exit 1
fi
if [ "$OUTPUT" == "" ]; then
    echo Failed to provide an output folder
    exit 1
fi

if [ $SINGULARITY == 1 ]; then 
    singularity exec --bind ./HMC_isolated.py:/mnt/HMC_isolated.py \
                    --bind ./antsMotCor.sh:/mnt/antsMotCor.sh \
                    --bind $INPUT:/mnt/input \
                    --bind $OUTPUT:/mnt/output \
                    ../../Fall2022/rabies.sif \
                    python /mnt/HMC_isolated.py /mnt/input /mnt/output $DATASET $LATEST_ANTS -c
else
    python ./HMC_isolated.py $INPUT $OUTPUT $DATASET $LATEST_ANTS
fi