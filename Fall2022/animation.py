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
