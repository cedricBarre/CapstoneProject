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

import subprocess, argparse, sys, glob, os, csv, json
import SimpleITK as sitk
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt

NIFTI_UNITS_METER = 1 # Meter
NIFTI_UNITS_MM = 2 # Millimeter
NIFTI_UNITS_MICRON = 3 # Micrometer
NIFTI_UNITS_SEC = 8 # Seconds
NIFTI_UNITS_MSEC = 16 # Milliseconds
NIFTI_UNITS_USEC = 24 # Microseconds
NIFTI_SPACE_MASK = 0x03
NIFTI_TIME_MASK = 0x18

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
    parser.add_argument('-p', '--performance', action='store_true', help='Specify this option to run the performance optimized version of the new ANTs motion correction')

    return parser.parse_args()


    #from rabies.utils
def copyInfo_3DImage(image_3d, ref_3d):
    if ref_3d.GetDimension() == 4:
        image_3d.SetSpacing(ref_3d.GetSpacing()[:3])
        image_3d.SetOrigin(ref_3d.GetOrigin()[:3])
        dim_3d = list(ref_3d.GetDirection())
        image_3d.SetDirection(tuple(dim_3d[:3]+dim_3d[4:7]+dim_3d[8:11]))
    elif ref_3d.GetDimension() == 3:
        image_3d.SetSpacing(ref_3d.GetSpacing())
        image_3d.SetOrigin(ref_3d.GetOrigin())
        image_3d.SetDirection(ref_3d.GetDirection())
    else:
        raise ValueError('Unknown reference image dimensions.')
    return image_3d

#from rabies.visualisation
def plot_3d(axes,sitk_img,fig,vmin=0,vmax=1,cmap='gray', alpha=1, cbar=False, threshold=None, planes=('sagittal', 'coronal', 'horizontal'), num_slices=4, slice_spacing=0.1):
    physical_dimensions = (np.array(sitk_img.GetSpacing())*np.array(sitk_img.GetSize()))[::-1] # invert because the array is inverted indices
    array=sitk.GetArrayFromImage(sitk_img)

    array[array==0]=None # set 0 values to be empty

    if not threshold is None:
        array[np.abs(array)<threshold]=None

    slice_0 = (1.0-((num_slices-1)*slice_spacing))/2
    slice_fractions=[slice_0]
    for i in range(1,num_slices):
        slice_fractions.append(slice_0+(i*slice_spacing))

    cbar_list = []
    
    ax_number=0
    if 'sagittal' in planes:
        ax=axes[ax_number]
        ax_number+=1
        empty_slice = np.array([np.nan]).repeat(array.shape[0])[:,np.newaxis]
        slices=empty_slice
        for s in slice_fractions:
            slice=array[::-1,:,int(array.shape[2]*s)]
            slices=np.concatenate((slices,slice,empty_slice),axis=1)
        pos = ax.imshow(slices, extent=[0,physical_dimensions[1]*num_slices,0,physical_dimensions[0]], vmin=vmin, vmax=vmax,cmap=cmap, alpha=alpha, interpolation='none')
        ax.axis('off')
        if cbar:
            cbar_list.append(fig.colorbar(pos, ax=ax))

    if 'coronal' in planes:
        ax=axes[ax_number]
        ax_number+=1
        empty_slice = np.array([np.nan]).repeat(array.shape[0])[:,np.newaxis]
        slices=empty_slice
        for s in slice_fractions:
            slice=array[::-1,int(array.shape[1]*s),:]
            slices=np.concatenate((slices,slice,empty_slice),axis=1)
        pos = ax.imshow(slices, extent=[0,physical_dimensions[2]*num_slices,0,physical_dimensions[0]], vmin=vmin, vmax=vmax,cmap=cmap, alpha=alpha, interpolation='none')
        ax.axis('off')
        if cbar:
            cbar_list.append(fig.colorbar(pos, ax=ax))

    if 'horizontal' in planes:
        ax=axes[ax_number]
        ax_number+=1
        empty_slice = np.array([np.nan]).repeat(array.shape[1])[:,np.newaxis]
        slices=empty_slice
        for s in slice_fractions:
            slice=array[int(array.shape[0]*s),::-1,:]
            slices=np.concatenate((slices,slice,empty_slice),axis=1)
        pos = ax.imshow(slices, extent=[0,physical_dimensions[2]*num_slices,0,physical_dimensions[1]], vmin=vmin, vmax=vmax,cmap=cmap, alpha=alpha, interpolation='none')
        ax.axis('off')
        if cbar:
            cbar_list.append(fig.colorbar(pos, ax=ax))
    return cbar_list

def hmcAnalysis(moving, scan_info, output, mask):
    print(f"Running analysis with the following inputs:\n" 
            f" - Moving image = {moving}\n"
            f" - Scan info = {scan_info}\n"
            f" - Output folder = {output}")
    
    motcorr_csv = os.path.join(output, "motcorrMOCOparams.csv")
    movparams_csv = os.path.join(output, "mov_params.csv")
    temporal_features = os.path.join(output, "temporal_features.png")
    FD_csv = os.path.join(output, "FD_calculations.csv")
    fitting_params_csv = os.path.join(output, "lin_reg_params.csv")
    analysis_data_csv = os.path.join(output, "analysis_data.csv")
    movparams_fieldnames = ['Euler rotation about X', 'Euler rotation about Y', 'Euler rotation about Z', 
                           'Translation in X', 'Translation in Y', 'Translation in Z']
    scan_params_fieldnames = ['Subject ID', 'Pixel Volume (mm^3)', 'Repetition Time (s)', 'Echo Time (s)', 
                                'Drift Rotation X', 'Drift Rotation Y', 'Drift Rotation Z',
                                'Drift Translation X', 'Drift Translation Y', 'Drift Translation Z', 
                                'Drift Framewise', 'Framewise Displacement STD', 'Mean of STD Difference', 
                                'Algorithm Version' ]
    warped_output = os.path.join(output, "motcorr_warped.nii.gz")
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
    
    fig,axes = plt.subplots(nrows=3, ncols=4, figsize=(30,10))

    # Linear fitting of the parameters
    lin_reg_params = []
    x_1 = range(0, len(motion_np[0, 1:]))
    for mot_param in motion_np:
        A = np.vstack([x_1, np.ones(len(x_1))]).T
        m, c = np.linalg.lstsq(A, mot_param[1:].astype(np.float64), rcond=None)[0]
        lin_reg_params.append([m, c])
    
    # Linear fitting framewise displacement
    x_2 = range(0, len(fd_np[1:]))
    A = np.vstack([x_2, np.ones(len(x_2))]).T
    m, c = np.linalg.lstsq(A, fd_np[1:].astype(np.float64), rcond=None)[0]
    lin_reg_params.append([m, c])

    with open(fitting_params_csv, 'w') as fitting_params_fp:
        fitting_w = csv.writer(fitting_params_fp, delimiter=',', quotechar='|')
        col_names = ['Parameter', 'm', 'c']
        res = np.vstack([np.asarray(movparams_fieldnames), 
                        np.asarray(lin_reg_params[0:6]).astype(np.float64).T[0], 
                        np.asarray(lin_reg_params[0:6]).astype(np.float64).T[1]]).T
        fitting_w.writerow(col_names)
        for row in res:
            fitting_w.writerow(row)
        fitting_w.writerow(['Framewise Displacement', lin_reg_params[6][0], lin_reg_params[6][1]])
    
    #Plot the Rotation and Translation parameters 
    rotations = axes[0,0]
    rotations.plot(motion_np[0, 1:].astype(np.float64), color='#0099ff', linestyle='solid')
    rotations.plot(motion_np[1, 1:].astype(np.float64), color='#ff9900', linestyle='solid')
    rotations.plot(motion_np[2, 1:].astype(np.float64), color='#00cc00', linestyle='solid')
    rotations.plot(x_1, lin_reg_params[0][0]*x_1 + lin_reg_params[0][1], color='#0099ff', linestyle='dashed')
    rotations.plot(x_1, lin_reg_params[1][0]*x_1 + lin_reg_params[1][1], color='#ff9900', linestyle='dashed')
    rotations.plot(x_1, lin_reg_params[2][0]*x_1 + lin_reg_params[2][1], color='#00cc00', linestyle='dashed')
    rotations.legend(movparams_fieldnames[0:3])
    rotations.set_title('Rotation parameters of each frame with reference to the average frame', fontsize=10, color='black')
    translations = axes[1,0]
    translations.plot(motion_np[3, 1:].astype(np.float64), color='#0099ff', linestyle='solid')
    translations.plot(motion_np[4, 1:].astype(np.float64), color='#ff9900', linestyle='solid')
    translations.plot(motion_np[5, 1:].astype(np.float64), color='#00cc00', linestyle='solid')
    translations.plot(x_1, lin_reg_params[3][0]*x_1 + lin_reg_params[3][1], color='#0099ff', linestyle='dashed')
    translations.plot(x_1, lin_reg_params[4][0]*x_1 + lin_reg_params[4][1], color='#ff9900', linestyle='dashed')
    translations.plot(x_1, lin_reg_params[5][0]*x_1 + lin_reg_params[5][1], color='#00cc00', linestyle='dashed')
    translations.legend(movparams_fieldnames[3:6])
    translations.set_title('Translation parameters of each frame with reference to the average frame', fontsize=10, color='black')

    # Plot the FD
    fd = axes[2,0]
    fd.plot(fd_np[1:].astype(np.float64), color='#0099ff', linestyle='solid')
    fd.plot(x_2, lin_reg_params[6][0]*x_2 + lin_reg_params[6][1], color='#0099ff', linestyle='dashed')
    fd.set_yticks(np.arange(0, 0.03, 0.005))
    fd.set_title('Framewise displacement of each frame with reference to the average frame', fontsize=10, color='black')

    #Calculate and plot the SNR and STD
    mask_img = sitk.ReadImage(mask, 8)
    mask_arr = sitk.GetArrayFromImage(mask_img)

    img_i = sitk.ReadImage(moving, 8)
    array_i = sitk.GetArrayFromImage(img_i)
    std_i = array_i.std(axis=0)
    std_i_filename = os.path.join(output, 'inputSTD.nii.gz')
    std_image_i = copyInfo_3DImage(
        sitk.GetImageFromArray(std_i, isVector=False), img_i)
    sitk.WriteImage(std_image_i, std_i_filename)

    img_o = sitk.ReadImage(warped_output, 8)
    array_o = sitk.GetArrayFromImage(img_o)
    std_o = array_o.std(axis=0)
    std_o_filename = os.path.join(output, 'outputSTD.nii.gz')
    std_image_o = copyInfo_3DImage(
        sitk.GetImageFromArray(std_o, isVector=False), img_o)
    sitk.WriteImage(std_image_o, std_o_filename)

    std_diff = np.subtract(std_i, std_o)
    mean_std_diff = np.mean(std_diff[mask_arr.astype(bool)])
    std_diff_filename = os.path.join(output, 'diffSTD.nii.gz')
    std_image_diff = copyInfo_3DImage(
        sitk.GetImageFromArray(std_diff, isVector=False), img_o)
    sitk.WriteImage(std_image_diff, std_diff_filename)

    axes[0,1].set_title('Temporal STD of Input BOLD', fontsize=20, color='black')
    std_i=std_i.flatten()
    std_i.sort()
    std_i_vmax = std_i[int(len(std_i)*0.95)]
    plot_3d(axes[:,1],std_image_i,fig=fig,vmin=0,vmax=std_i_vmax,cmap='inferno', cbar=True)
    axes[0,2].set_title('Temporal STD of Corrected\nTimeseries', fontsize=20, color='black')
    std_o=std_o.flatten()
    std_o.sort()
    std_o_vmax = std_o[int(len(std_o)*0.95)]
    plot_3d(axes[:,2],std_image_o,fig=fig,vmin=0,vmax=std_o_vmax,cmap='inferno', cbar=True)
    axes[0,3].set_title('Temporal STD Difference', fontsize=20, color='black')
    std_diff=std_diff.flatten()
    std_diff.sort()
    std_diff_vmax = std_diff[int(len(std_diff)*0.95)]
    plot_3d(axes[:,3],std_image_diff,fig=fig,vmin=0,vmax=std_diff_vmax,cmap='inferno', cbar=True)

    fig.savefig(temporal_features)

    # Extract useful parameters of the initial moving timeseries
    with open(scan_info, 'r') as scan_info_fp, open(analysis_data_csv, 'w') as analysis_data_fp:
        scan_params_w = csv.writer(analysis_data_fp, delimiter=',', quotechar='|')
        moving_obj = nb.load(moving)
        xyzt_units = moving_obj.header['xyzt_units']
        space_unit = 1
        time_unit = 1
        algo_version = 'new' if(os.path.exists(os.path.join(output, "new_ants.txt"))) else 'old'
        fd_std = np.std(fd_np.astype(np.float64))
        NA1, xdim, ydim, zdim, tdim, NA2, NA3, NA4 = moving_obj.header['pixdim']
        if(xyzt_units & NIFTI_SPACE_MASK == NIFTI_UNITS_METER):
            space_unit = 1000
        elif (xyzt_units & NIFTI_SPACE_MASK == NIFTI_UNITS_MICRON):
            space_unit = 1
        elif (xyzt_units & NIFTI_SPACE_MASK != NIFTI_UNITS_MM):
            print("[ WARNING ] - Failed to establish the space dimension unit of the pixel")
        if(xyzt_units & NIFTI_TIME_MASK == NIFTI_UNITS_MSEC):
            time_unit = 0.001
        elif (xyzt_units & NIFTI_TIME_MASK == NIFTI_UNITS_USEC):
            time_unit = 0.000001
        elif (xyzt_units & NIFTI_TIME_MASK != NIFTI_UNITS_SEC):
            print("[ WARNING ] - Failed to establish the space dimension unit of the pixel")
        row = np.hstack([int(os.path.basename(scan_info)[4:7]),
                xdim * space_unit * ydim * space_unit * zdim * space_unit,
                tdim * time_unit,
                json.load(scan_info_fp)['EchoTime'],
                np.asarray(lin_reg_params).astype(np.float64).T[0],
                fd_std, mean_std_diff, algo_version])
        scan_params_w.writerow(scan_params_fieldnames)
        scan_params_w.writerow(row)

def executeANTsMotionCorr(moving, reference, mask, output, latest_ants, containerized, performance):
    print(f"Executing ANTS motion correction with the following inputs:\n" 
            f" - Moving = {moving}\n"
            f" - Reference = {reference}\n"
            f" - Mask = {mask}\n"
            f" - Output folder = {output}")
    
    motcor_path = './'

    latest_ants_opt = ""
    if latest_ants:
        latest_ants_opt = '-l'
    
    containerized_opt = ""
    if containerized:
        containerized_opt = '-c'
        motcor_path = "/mnt/"
    
    performance_opt = ""
    if performance:
        performance_opt = '-p'
    
    command = f"{motcor_path}antsMotCor.sh -m {moving} -r {reference} -x {mask} -o {output} {latest_ants_opt} {containerized_opt} {performance_opt}"
    process = subprocess.Popen( command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True )
    while True:
        out = process.stdout.read(1)
        if process.poll() != None:
            break
        if out != '':
            sys.stdout.write(out.decode("utf-8", 'replace'))
            sys.stdout.flush()

def hmcMain(input_folder : str, output_folder : str, dataset : bool, latest_ants : bool, containerized : bool, performance : bool):
    if not dataset:
        moving = glob.glob(os.path.join(input_folder, "ses-1/func/*.nii.gz"))
        mask = glob.glob(os.path.join(input_folder, f"ses-1/func/_scan_info_subject_id*/*mask.nii.gz"))
        if len(moving) == 0:
            print(f"Failed to find the moving images nifti file in subject folder ses-1/func")
            return
        if len(mask) == 0:
                print(f"Failed to find the mask nifti file in subject folder /ses-1/func")
                return
        if not os.path.exists(os.path.join(output_folder, "motcorrMOCOparams.csv")):
            reference = glob.glob(os.path.join(input_folder,"ses-1/func/_scan_info_subject_id*/*ref.nii.gz"))
            if len(reference) == 0:
                print(f"Failed to find the reference nifti file in subject folder ses-1/func")
                return
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            executeANTsMotionCorr(moving[0], reference[0], mask[0], output_folder, latest_ants, containerized, performance)
        else:
            print(f"Output files already present in folder {output_folder}, skipping motion correction.")
        
        scan_info = glob.glob(os.path.join(input_folder, "ses-1/func/*.json"))
        if len(scan_info) == None:
                print(f"Failed to find the scan info json file in subject folder ses-1/func")
                return 
        hmcAnalysis(moving[0], scan_info[0], output_folder, mask[0])
    else:
        all_subjects = glob.glob(os.path.join(input_folder, "sub-*/"))
        commands  = []

        if len(all_subjects) == 0:
            print("No subjects found in dataset. Finishing job.")
            return

        for subject in all_subjects:
            sub_name = subject.split('/')[-1] if subject.split('/')[-1] != '' else subject.split('/')[-2]
            sub_num  = sub_name.split('-')[-1]
            sub_output_folder = os.path.join(output_folder, sub_name + "/old_ants")
            print(f"\n+ PROCESSING SUBJECT {sub_num} --------------------------------------------------------------+")
            moving = glob.glob(os.path.join(subject, "ses-1/func/*.nii.gz"))
            mask = glob.glob(os.path.join(subject, f"ses-1/func/_scan_info_subject_id{sub_num}*/*mask.nii.gz"))
            if len(moving) == 0:
                print(f"Failed to find the moving images nifti file in subject folder {subject}/ses-1/func")
                return 
            if len(mask) == 0:
                    print(f"Failed to find the mask nifti file in subject folder {subject}/ses-1/func")
                    return
            
            if not os.path.exists(os.path.join(sub_output_folder, "motcorrMOCOparams.csv")):
                reference = glob.glob(os.path.join(subject, f"ses-1/func/_scan_info_subject_id{sub_num}*/*ref.nii.gz"))
                if len(reference) == 0:
                    print(f"Failed to find the reference nifti file in subject folder {subject}/ses-1/func")
                    return
                if not os.path.exists(sub_output_folder):
                    os.makedirs(sub_output_folder)
                command = executeANTsMotionCorr(moving[0], reference[0], mask[0], sub_output_folder, latest_ants, containerized, performance)
            else:
                print(f"Output files already present in folder {sub_output_folder}, skipping motion correction.")
            
            scan_info = glob.glob(os.path.join(subject, "ses-1/func/*.json"))
            if len(scan_info) == 0:
                print(f"Failed to find the scan info json file in subject folder {subject}/ses-1/func")
                return
            hmcAnalysis(moving[0], scan_info[0], sub_output_folder, mask[0])
        
if __name__ == "__main__":
    print("Running HMC in isolation...")
    args = parseArguments()

    hmcMain(args.input_folder, args.output_folder, args.dataset, args.latest_ants, args.containerized, args.performance)