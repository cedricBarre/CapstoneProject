#!/bin/bash
START=0
END=0
FOLDER=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -f)
      FOLDER="$2"
      shift # past argument
      shift # past value
      ;;
    -s)
      START="$2"
      shift # past argument
      shift # past value
      ;;
    -e)
      END="$2"
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

if [ "$START" == "0" ]; then
    echo Failed to provide start param
    exit 1
fi
if [ "$END" == "0" ]; then
    echo Failed to provide end param
    exit 1
fi
if [ "$FOLDER" == "" ]; then
    echo Failed to provide fodler param
    exit 1
fi

subjects=($(seq -f "%03g" $START $END))

cd $FOLDER

for num in "${subjects[@]}"
do
  mkdir -p sub-$num/ses-1/func
  mv sub-$num* sub-$num/ses-1/func
  mv _scan_info_subject_id$num* sub-$num/ses-1/func
  # sshpass -p Cedvick28 rsync -avz -e 'ssh -p 2222' barced@gateway.douglasneuroinformatics.ca:/data/scratch2/cedric/Fall2022/data/HMC_output/rabies_7_Cryo_med_f1/sub-$num/new_ants ./sub-$num/
done