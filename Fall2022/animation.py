'''

    Python script used to run the animation to help detect motion 

'''

import subprocess, argparse, sys, glob, os, csv
import SimpleITK as sitk
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt


def animation(QPP_reshaped):
    # example of plotting a 4D nifti across time, using the QPP image
    # QPP_reshaped: a 4D nifti file loaded into a 2D time X voxel array

    # the 3D voxel dimensions were transformed into a vector using the brain mask shape, so we need to retransform it into a 4D array
    mask_file='mask.nii.gz' # brain mask
    mask=np.asarray(nb.load(mask_file).dataobj)
    shape=mask.shape
    mask_vector=np.zeros([QPP_reshaped.shape[0],len(mask.reshape(-1))])
    mask_indices=(mask.reshape(-1)==True)
    data_array=np.zeros([QPP_reshaped.shape[0],shape[0],shape[1],shape[2]])
    for i in range(QPP_reshaped.shape[0]):
        mask_vector[i,mask_indices]=QPP_reshaped[i,:]
        data_array[i,:,:,:]=mask_vector[i,:].reshape(shape)

#Result: we have a 3D image now in data array
    from nilearn.plotting import plot_stat_map
    # First set up the figure, the axis, and the plot element we want to animate
    import matplotlib.animation as animation
    fig,ax = plt.subplots(nrows=1, ncols=1,figsize=(10,10))
    plt.title('Coronal view', fontsize=30)
    plt.axis('off')
    vmax=np.abs(data_array).max()
    vmin=-vmax

    #instead of imshow, I need to find another funciton in RABIES

    # initialization function: plot the background of each frame
    def init():
        line=ax.imshow(data_array[0,:,40,::-1].T, cmap='cold_hot',vmax=vmax,vmin=vmin)
        return [line]

    # animation function.  This is called sequentially
    def animate(i):
        line=ax.imshow(data_array[i,:,40,::-1].T, cmap='cold_hot',vmax=vmax,vmin=vmin)
        return [line]

    num_frames=10
    # call the animator. blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=num_frames, #fargs=(QPP_reshaped),
                                    interval=500, blit=True, repeat_delay=5000)

    from matplotlib import animation, rc
    from IPython.display import HTML
    HTML(anim.to_html5_video())

    #for IPython we shall pip install IPython
    
    
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
