#!/bin/bash

singularity exec --bind ./:/mnt/ ../../Fall2022/rabies.sif python /mnt/HMC_isolated.py

#singularity exec --bind ./:/mnt/ ../../Fall2022/rabies.sif antsMotionCorr --help