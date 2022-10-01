'''
     _   _  __  __  ___    ____  ___  _____  __      __   ____  ____  ____  
    ( )_( )(  \/  )/ __)  (_  _)/ __)(  _  )(  )    /__\ (_  _)( ___)(  _ \ 
     ) _ (  )    (( (__    _)(_ \__ \ )(_)(  )(__  /(__)\  )(   )__)  )(_) )
    (_) (_)(_/\/\_)\___)  (____)(___/(_____)(____)(__)(__)(__) (____)(____/ 

    Python script used to run the ANTs motion correction algorithm in isolation
    from the RABIES preprocessing pipeline. This script will allow us to excite 
    the ANTs algorithm with various datasets and obtain the raw output to evaluate 
    relationships between specific parameters in the input datasets and the effects
    on the outputs. 
'''

import subprocess, argparse
import SimpleITK as sitk

def parseArguments():
    parser = argparse.ArgumentParser(description='Head motion correction stage of RABIES pipeline preprocessing stage')
    parser.add_argument('moving', 
                        help='Name of moving 3D scan with temporal dimension')
    parser.add_argument('reference', 
                        help='Name of reference 3D scan')
    parser.add_argument('output', 
                        help='Output folder')

    return parser.parse_args()

def executeANTsMotionCorr(moving, reference, output):
    print(f"Moving input = {moving}, reference input = {reference} and output folder = {output}")

    moving_img = sitk.ReadImage(moving)
    n = moving_img.GetSize()[3]
    if (n > 10):
        n = 10
    command = f"antsMotionCorr -d 3 -o [{output}/motcorr,{output}/motcorr_warped.nii.gz,{output}/motcorr_avg.nii.gz] -m MI[ {reference} , \
                {moving} , 1 , 20 , regular, 0.2 ] -t Rigid[ 0.25 ] -i 50x20 -s 1x0 -f 2x1 -u 1 -e 1 -l 1 -n {str(n)}"

if __name__ == "__main__":
    print("Running HMC in isolation...")
    args = parseArguments()

    executeANTsMotionCorr(args.moving, args.reference, args.output)