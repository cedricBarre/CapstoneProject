'''
    Python script used to run the animation to help detect motion 
'''

import subprocess, argparse, sys, glob, os, csv
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation, rc
from IPython.display import HTML
import SimpleITK as sitk
#from rabies.visualization import plot_3d

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

def parseArguments():
    parser = argparse.ArgumentParser(description='Motion animation stage of analysis', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_folder', 
                        help="Input folder containing the subject to process. The folder can also be a dataset following\n"
                             "the BIDS hierarchy with the fMRI data of each subject. If the folder is a dataset, specify\n"
                             "the -d parameter. Each subject folder should respect the following format:\n"
                             "   sub-0XX\n"
                             "   └── ses-1\n"
                             "       └── func\n"
                             "           ├── _scan_info_subject_id0XX.session1.runNone_split_name_sub-0XX_ses-1_task-rest_acq-EPI_bold\n"
                             "           │   └── sub-0XX_ses-1_task-rest_acq-EPI_bold_bold_ref.nii.gz\n"
                             "           ├── sub-0XX_ses-1_func_sub-0XX_ses-1_task-rest_acq-EPI_bold.json\n"
                             "           └── sub-0XX_ses-1_task-rest_acq-EPI_bold.nii.gz\n"
                             "Here, XX represents the number of the subject\n")

    parser.add_argument('output_folder', 
                        help='Output folder')
    parser.add_argument('-d', '--dataset', action='store_true', help='Folder provided is a dataset folder following the BIDS hierarchy')

    return parser.parse_args()

#Function convert the nifti into a numpy array
def extractFile(path):
    sitk_image = sitk.ReadImage(path, sitk.sitkFloat32)
    return sitk_image

#Function that defines the animation 
def animationSubject(sitk_image, output_path):
    fig,axes = plt.subplots(nrows=3, ncols=1,figsize=(20,10))
    axes[0].set_title('Coronal view', fontsize=30, color='black')
    axes[1].set_title('Saggital view', fontsize=30, color='black')
    axes[2].set_title('Horizontal view', fontsize=30, color='black')
    plt.axis('off')
    
    array = sitk.GetArrayFromImage(sitk_image)
    vmax = array.max()
    num_frames= int(array.shape[0]/5) 
   
    #instead of imshow(), we use the RABBIES function plot_3D
    def init():
        line = plot_3d(axes[:],sitk_image[:,:,:,0],fig=fig,vmin=0,vmax=vmax,cmap='viridis', cbar=False,planes=('sagittal', 'coronal', 'horizontal'), num_slices=4)
        return line

    # animation function. This is called sequentially
    def animate(i):
        line = plot_3d(axes[:],sitk_image[:,:,:,i*5],fig=fig,vmin=0,vmax=vmax,cmap='viridis', cbar=False,planes=('sagittal', 'coronal', 'horizontal'), num_slices=4)
        return line

    # call the animator
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=500, blit=True, repeat_delay=5000)

    animation_output = os.path.join(output_path, "animation.mp4")
    writer_anim = animation.FFMpegWriter(fps=30) 
    anim.save(animation_output , writer=writer_anim)

def animationMain(input_folder, output_folder, dataset):
    #animate a single file
    if not dataset:
        moving = glob.glob(os.path.join(input_folder, "ses-1/func/*.nii.gz"))
        if len(moving) == 0:
            print(f"Failed to find the moving images nifti file in subject folder ses-1/func")
            return
        else: 
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            animationSubject(extractFile(moving[0]), output_folder)
    #animate an entire dataset
    else:
        all_subjects = glob.glob(os.path.join(input_folder, "sub-*/"))
        if len(all_subjects) == 0:
            print("No subjects found in dataset. Finishing job.")
            return
        for subject in all_subjects:
            sub_name = subject.split('/')[-1] if subject.split('/')[-1] != '' else subject.split('/')[-2]
            sub_num  = sub_name.split('-')[-1]
            sub_output_folder = os.path.join(output_folder, sub_name + "/animation")
            print(f"\n+ PROCESSING ANIMATION {sub_num} --------------------------------------------------------------+")
            moving = glob.glob(os.path.join(subject, "ses-1/func/*.nii.gz"))
            if len(moving) == 0:
                print(f"Failed to find the moving images nifti file in subject folder {subject}/ses-1/func")
                return 
            if not os.path.exists(sub_output_folder):
                    os.makedirs(sub_output_folder)
            animationSubject(extractFile(moving[0]), sub_output_folder)


if __name__ == "__main__":
    args = parseArguments()
    data = args.input_folder
    output = args.output_folder
    isDataSet = args.dataset
    animationMain(data, output, isDataSet)


