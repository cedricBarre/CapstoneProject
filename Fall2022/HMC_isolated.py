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

import subprocess, argparse, sys, glob, os, csv
import SimpleITK as sitk
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt

def parseArguments():
    parser = argparse.ArgumentParser(description='Head motion correction stage of RABIES pipeline preprocessing stage', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_folder', 
                        help="Input folder containing the subject to process. The folder can also be a dataset following\n"
                             "the BIDS hierarchy with the fMRI data of each subject. If the folder is a dataset, specify\n"
                             "the -d parameter. Each subject folder should respect the following format:\n"
                             "   sub-0XX\n"
                             "   └── ses-1\n"
                             "       └── func\n"
                             "           ├── _scan_info_subject_id0XX.session1.runNone_split_name_sub-0XX_ses-1_task-rest_acq-EPI_bold\n"
                             "           │   └── sub-0XX_ses-1_task-rest_acq-EPI_bold_bold_ref.nii.gz\n"
                             "           ├── sub-0XX_ses-1_func_sub-0XX_ses-1_task-rest_acq-EPI_bold.json\n"
                             "           └── sub-0XX_ses-1_task-rest_acq-EPI_bold.nii.gz\n"
                             "Here, XX represents the number of the subject\n")
    parser.add_argument('output_folder', 
                        help='Output folder')
    parser.add_argument('-d', '--dataset', action='store_true', help='Folder provided is a dataset folder following the BIDS hierarchy')
    parser.add_argument('-l', '--latest_ants', action='store_true', help='Specify to use latest install of ANTs motion correction')
    parser.add_argument('-c', '--containerized', action='store_true', help='Specify this option if we are running in a container')

    return parser.parse_args()

def hmcAnalysis(moving, scan_info, output):
    print(f"Running analysis with the following inputs:\n" 
            f" - Moving image = {moving}\n"
            f" - Scan info = {scan_info}\n"
            f" - Output folder = {output}")
    
    motcorr_csv = os.path.join(output, "motcorrMOCOparams.csv")
    movparams_csv = os.path.join(output, "mov_params.csv")
    temporal_features = os.path.join(output, "temporal_features.png")
    FD_csv = os.path.join(output, "FD_calculations.csv")
    movparams_fieldnames = ['Euler rotation about X', 'Euler rotation about Y', 'Euler rotation about Z', 
                           'Translation in X', 'Translation in Y', 'Translation in Z']
    motion_np = np.zeros((1,6)) 
    fd_np = np.zeros([0])

    with open(motcorr_csv, 'r') as motcorr_fp, open(movparams_csv, 'w') as movparams_fp, open(FD_csv, 'r') as FD_fp:
        motcorr_r   = csv.reader(motcorr_fp, delimiter=',', quotechar='|')
        movparam_w = csv.writer(movparams_fp, delimiter=',', quotechar='|')
        fd_r = csv.reader(FD_fp, delimiter=',', quotechar='|')
        movparam_w.writerow(movparams_fieldnames)
        idx = 0
        for row in motcorr_r:
            if idx != 0:
                movparam_w.writerow(row[2:len(row)])
                motion_np = np.vstack([motion_np, np.array(row[2:len(row)])])
            else:
                idx = idx + 1
        idx = 0
        for row in fd_r:
            if idx != 0:
                fd_np = np.hstack([fd_np, np.array(row[0])])
            else:
                idx = idx + 1

        motion_np = np.transpose(motion_np)
    
    fig,axes = plt.subplots(nrows=3, ncols=1, figsize=(20,5))
    
    rotations = axes[0]
    rotations.plot(motion_np[0, 1:].astype(np.float64))
    rotations.plot(motion_np[1, 1:].astype(np.float64))
    rotations.plot(motion_np[2, 1:].astype(np.float64))
    rotations.legend(movparams_fieldnames[0:3])
    rotations.set_title('Rotation parameters of each frame with reference to the average frame', fontsize=30, color='white')
    translations = axes[1]
    translations.plot(motion_np[3, 1:].astype(np.float64))
    translations.plot(motion_np[4, 1:].astype(np.float64))
    translations.plot(motion_np[5, 1:].astype(np.float64))
    translations.legend(movparams_fieldnames[3:6])
    translations.set_title('Translation parameters of each frame with reference to the average frame', fontsize=30, color='white')
    fd = axes[2]
    fd.plot(fd_np[1:].astype(np.float64))
    fd.set_title('Framewise displacement of each frame with reference to the average frame', fontsize=30, color='white')
    fig.savefig(temporal_features)


def executeANTsMotionCorr(moving, reference, output, latest_ants, containerized):
    print(f"Executing ANTS motion correction with the following inputs:\n" 
            f" - Moving = {moving}\n"
            f" - Reference = {reference}\n"
            f" - Output folder = {output}")
    
    latest_ants_opt = ""
    if latest_ants:
        latest_ants_opt = '-l'
    
    containerized_opt = ""
    if containerized:
        containerized_opt = '-c'
    
    command = f"./antsMotCor.sh -m {moving} -r {reference} -o {output} {latest_ants_opt} {containerized_opt}"
    process = subprocess.Popen( command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True )
    while True:
        out = process.stdout.read(1)
        if process.poll() != None:
            break
        if out != '':
            sys.stdout.write(out.decode("utf-8", 'replace'))
            sys.stdout.flush()

def hmcMain(input_folder : str, output_folder : str, dataset : bool, latest_ants : bool, containerized : bool):
    if not dataset:
        moving = glob.glob(os.path.join(input_folder, "ses-1/func/*.nii.gz"))
        if len(moving) == 0:
            print(f"Failed to find the moving images nifti file in subject folder ses-1/func")
            return
        if not os.path.exists(os.path.join(output_folder, "mov_params.csv")):
            reference = glob.glob(os.path.join(input_folder,"ses-1/func/_scan_info_subject_id*/*.nii.gz"))
            if len(reference) == 0:
                print(f"Failed to find the reference nifti file in subject folder ses-1/func")
                return
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            executeANTsMotionCorr(moving[0], reference[0], output_folder, latest_ants, containerized)
        else:
            print(f"Output files already present in folder {output_folder}, skipping motion correction.")
        
        scan_info = glob.glob(os.path.join(input_folder, "ses-1/func/*.json"))
        if len(scan_info) == None:
                print(f"Failed to find the scan info json file in subject folder ses-1/func")
                return 
        hmcAnalysis(moving[0], scan_info[0], output_folder)
    else:
        all_subjects = glob.glob(os.path.join(input_folder, "sub-*/"))

        if len(all_subjects) == 0:
            print("No subjects found in dataset. Finishing job.")
            return
        
        for subject in all_subjects:
            sub_name = subject.split('/')[-1] if subject.split('/')[-1] != '' else subject.split('/')[-2]
            sub_num  = sub_name.split('-')[-1]
            sub_output_folder = os.path.join(output_folder, sub_name)
            print(f"\n+ PROCESSING SUBJECT {sub_num} --------------------------------------------------------------+")
            moving = glob.glob(os.path.join(subject, "ses-1/func/*.nii.gz"))
            if len(moving) == 0:
                print(f"Failed to find the moving images nifti file in subject folder {subject}/ses-1/func")
                return 
            
            if not os.path.exists(os.path.join(sub_output_folder, "mov_params.csv")):
                reference = glob.glob(os.path.join(subject, f"ses-1/func/_scan_info_subject_id{sub_num}*/*.nii.gz"))
                if len(reference) == 0:
                    print(f"Failed to find the reference nifti file in subject folder {subject}/ses-1/func")
                    return
                if not os.path.exists(sub_output_folder):
                    os.makedirs(sub_output_folder)
                executeANTsMotionCorr(moving[0], reference[0], sub_output_folder, latest_ants, containerized)
            else:
                print(f"Output files already present in folder {sub_output_folder}, skipping motion correction.")
            
            scan_info = glob.glob(os.path.join(subject, "ses-1/func/*.json"))
            if len(scan_info) == 0:
                    print(f"Failed to find the scan info json file in subject folder {subject}/ses-1/func")
                    return
            hmcAnalysis(moving[0], scan_info[0], sub_output_folder)

if __name__ == "__main__":
    print("Running HMC in isolation...")
    args = parseArguments()

    hmcMain(args.input_folder, args.output_folder, args.dataset, args.latest_ants, args.containerized)