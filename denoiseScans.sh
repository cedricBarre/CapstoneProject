#!/bin/bash
module load ANTs
module load minc-toolkit

filename="$1"

if [ "${filename##*.}" != "mnc" ] ; then
    echo Not equals ${filename##*.}
else
    echo Equals ${filename##*.}
fi
