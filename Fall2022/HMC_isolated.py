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

import subprocess, argparse, sys, glob, os
import SimpleITK as sitk
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt

def parseArguments():
    parser = argparse.ArgumentParser(description='Head motion correction stage of RABIES pipeline preprocessing stage')
    parser.add_argument('input_folder', 
                        help='Input folder containing the subjects to process. The folder provided follows a BIDS'
                                ' hierarchy with the fMRI data of each subject.')
    parser.add_argument('output_folder', 
                        help='Output folder')

    return parser.parse_args()

def hmcAnalysis(moving, scan_info, output):
    print(f"Running analysis with the following inputs:\n" 
            f" - Moving image = {moving}\n"
            f" - Scan info = {scan_info}\n"
            f" - Output folder = {output}")

def executeANTsMotionCorr(moving, reference, output):
    print(f"Executing ANTS motion correction with the following inputs:\n" 
            f" - Moving = {moving}\n"
            f" - Reference = {reference}\n"
            f" - Output folder = {output}")

    moving_img = sitk.ReadImage(moving)
    n = moving_img.GetSize()[3]
    if (n > 10):
        n = 10
    
    command = f"antsMotionCorr -d 3 -o [{output}/motcorr,{output}/motcorr_warped.nii.gz,{output}/motcorr_avg.nii.gz] -m MI[ {reference} , \
                {moving} , 1 , 20 , regular, 0.2 ] -t Rigid[ 0.25 ] -i 50x20 -s 1x0 -f 2x1 -u 1 -e 1 -l 1 -n {str(n)} -v 1"
    process = subprocess.Popen( command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True )
    while True:
        out = process.stdout.read(1)
        if process.poll() != None:
            break
        if out != '':
            sys.stdout.write(out.decode("utf-8", 'replace'))
            sys.stdout.flush()

def hmcMain(input_folder, output_folder):
    all_subjects = glob.glob(os.path.join(input_folder, "sub-*/"))
    
    for subject in all_subjects:
        sub_name = subject.split('/')[-1] if subject.split('/')[-1] != '' else subject.split('/')[-2]
        sub_num  = sub_name.split('-')[-1]
        sub_output_folder = os.path.join(output_folder, sub_name)
        print(f"\n+ PROCESSING SUBJECT {sub_num} --------------------------------------------------------------+")
        moving = glob.glob(os.path.join(subject, "ses-1/func/*.nii.gz"))
        if moving[0] == None:
            print(f"Failed to find the moving images nifti file in subject folder {subject}/ses-1/func")
        
        if not os.path.exists(os.path.join(sub_output_folder, "motcorrMOCOparams.csv")):
            reference = glob.glob(os.path.join(subject, f"ses-1/func/_scan_info_subject_id{sub_num}*/*.nii.gz"))
            if reference[0] == None:
                print(f"Failed to find the reference nifti file in subject folder {subject}/ses-1/func")
            if not os.path.exists(sub_output_folder):
                os.makedirs(sub_output_folder)
            executeANTsMotionCorr(moving[0], reference[0], sub_output_folder)
        else:
            print(f"Output files already present in folder {sub_output_folder}, skipping motion correction.")
        
        scan_info = glob.glob(os.path.join(subject, "ses-1/func/*.json"))
        if scan_info[0] == None:
                print(f"Failed to find the scan info json file in subject folder {subject}/ses-1/func")
        hmcAnalysis(moving[0], scan_info[0], sub_output_folder)

if __name__ == "__main__":
    print("Running HMC in isolation...")
    args = parseArguments()

    hmcMain(args.input_folder, args.output_folder)