# Useful Imports
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt
import csv
import subprocess
import os
import shutil
import sys
import math

# Global variable declaration
OUTPUT_DIR = "output"
MINC_FILES_DIR = "output/minc_files"
NIFTI_FILES_DIR = "output/nifti_files"
DENOISED_FILES_DIR = "output/denoised"
MASK_FILES_DIR = "output/masks"
TRANSFORMS_DIR = "output/transforms_from_subject_to_atlas"
BIAS_CORRECTED_DIR = "output/n4_bias_corrected"

def findRatios(maskfile):
    data = {}

    # buildOutputDir()

    # Set up the scan data list
    with open('scans.csv', newline='') as scanfile:
        reader = csv.DictReader(scanfile)
        for row in reader:
            shutil.copy(row['file_name'], NIFTI_FILES_DIR + '/' + row['rg_value'].replace('.', '_'))
            data[row['rg_value']] = [ [], []]

    # Call segmentation script to remove the background of the scan
    mask_reference_file = os.listdir(NIFTI_FILES_DIR + "/101")[0] # Choose one RG 101 file to be the reference for the mask creation
    mask_reference_file = os.path.join(NIFTI_FILES_DIR + "/101", mask_reference_file)
    existing_mask = '' if maskfile == None else maskfile # Will bypass mask creation if a mask file is supplied already
    p = subprocess.Popen("./segmentBrain.sh {} {} {} {}".format(mask_reference_file, MINC_FILES_DIR, OUTPUT_DIR, existing_mask),
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(p.poll() is None):
        line = p.stdout.readline().decode('utf-8')
        if(len(line) != 0):
            print(line)

    # Load mask
    mask = np.asarray(nb.load((MASK_FILES_DIR + "/PDw_mask.nii.gz") if maskfile == None else maskfile).dataobj)

    # Get all directories in the denoised directory since the denoised scans are sorted in directories correpsonding to their rg value
    for sorted_dir in os.listdir(DENOISED_FILES_DIR):
        sorted_dir_path = os.path.join(DENOISED_FILES_DIR, sorted_dir)
        if os.path.isdir(sorted_dir_path):
            # Get all the scan file names in each sorted directory
            scan_list = os.listdir(sorted_dir_path)
            scan_amount = len(scan_list)
            rg = os.path.basename(os.path.normpath(sorted_dir)).replace("_", ".") # Get RG value from directory
            datarow = data[rg] # Access the right key in the directory depending on the RG value
            # Create numpy array to hold all scans (useful if we want to print any of the scans later, not used for now)
            datarow[0] = np.zeros((scan_amount, mask.shape[0], mask.shape[1], mask.shape[2])) 
            datarow[1] = [0] * scan_amount # Create array to hold mean intensity for each scan
            idx = 0
            # For each scan in the directory...
            for denoised_scan in scan_list:
                file_path = os.path.join(sorted_dir_path, denoised_scan)
                scan_array = np.asarray(nb.load(file_path).dataobj) # Load the scan as a numpy array
                # Save in the array of scan array (useful if we want to print any of the scans later, not used for now)
                datarow[0][idx, :, :, :] = scan_array
                datarow[1][idx] = np.mean(scan_array[mask.astype(bool)]) # Calculate the mean of all voxels inside the brain
                idx = idx + 1
            data[rg] = datarow # Save value of the RG key in the dictionary 
    
    # Calculate the ratio for each pair of RG with the reference RG of 101. Here we assume that each RG value has the
    # same amount of scans so we can use np.divide to divide the arrays containing the mean intensities for each scan
    # of each RG value
    ratio_data = [ np.divide(data["101"][1], data["90.5"][1]), np.divide(data["101"][1], data["80.6"][1]), 
                    np.divide(data["101"][1], data["71.8"][1]), np.divide(data["101"][1], data["64"][1]), 
                    np.divide(data["101"][1], data["50.8"][1]) ]
    
    average_data = [ np.mean(ratio_data[0]), np.mean(ratio_data[1]), np.mean(ratio_data[2]),
                        np.mean(ratio_data[3]), np.mean(ratio_data[4]) ]
    
    # Print results
    print("+---------------+------------+------------+------------+------------+------------+\n" +
          "|               |  101/90.5  |  101/80.6  |  101/71.8  |  101/64.0  |  101/50.8  |\n" +
          "+---------------+------------+------------+------------+------------+------------+\n" +
          "|   First Pair  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |\n".format(
                                                                            round(ratio_data[0][0], 6),
                                                                            round(ratio_data[1][0], 6),
                                                                            round(ratio_data[2][0], 6),
                                                                            round(ratio_data[3][0], 6),
                                                                            round(ratio_data[4][0], 6)) +
          "+---------------+------------+------------+------------+------------+------------+\n" +
          "|  Second Pair  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |\n".format(
                                                                            round(ratio_data[0][1], 6),
                                                                            round(ratio_data[1][1], 6),
                                                                            round(ratio_data[2][1], 6),
                                                                            round(ratio_data[3][1], 6),
                                                                            round(ratio_data[4][1], 6)) +
          "+---------------+------------+------------+------------+------------+------------+\n" +
          "|   Third Pair  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |\n".format(
                                                                            round(ratio_data[0][2], 6),
                                                                            round(ratio_data[1][2], 6),
                                                                            round(ratio_data[2][2], 6),
                                                                            round(ratio_data[3][2], 6),
                                                                            round(ratio_data[4][2], 6)) +
          "+---------------+------------+------------+------------+------------+------------+\n" +
          "|    Average    |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |\n".format(
                                                                            round(average_data[0], 6),
                                                                            round(average_data[1], 6),
                                                                            round(average_data[2], 6),
                                                                            round(average_data[3], 6),
                                                                            round(average_data[4], 6)) +
          "+---------------+------------+------------+------------+------------+------------+")

    # Plot the pair data points
    x = ['101/50.8', '101/64', '101/71.8', '101/80.6', '101/90.5']
    y = np.asarray([ratio_data[4] / (101/50.8), ratio_data[3] / (101/64), ratio_data[2] / (101/71.8), 
            ratio_data[1] / (101/80.6), ratio_data[0] / (101/90.5) ])
    y1 = y.T[0]
    y2 = y.T[1]
    y3 = y.T[2]
    fig = plt.figure(3, figsize=(10, 6))
    xscale = np.array([0, 1, 2, 3, 4])
    plt.yticks(np.arange(0.95, 1.2, 0.01))
    plt.xticks(xscale, x)
    p = plt.plot(x, y1, 'ko', linestyle="None")
    p = plt.plot(x, y2, 'ko', linestyle="None")
    p = plt.plot(x, y3, 'ko', linestyle="None")
    plt.xlabel("RG Ratios")
    plt.ylabel("Mean intensity values normalized by the expected RG values")
    plt.grid()
    plt.savefig(OUTPUT_DIR + "/ratio_pair_plot.jpg")

    # Prepare the final plot
    fig = plt.figure(4, figsize=(10, 6))
    xscale = np.array([0, 1, 2, 3, 4])
    # Calculate error as standard deviation of the 3 data points divided by the square root of the amount of data points (3)
    error = [ np.std(y[0]) / math.sqrt(len(y[0])), np.std(y[1]) / math.sqrt(len(y[1])), 
                np.std(y[2]) / math.sqrt(len(y[2])), np.std(y[3]) / math.sqrt(len(y[3])), 
                np.std(y[4]) / math.sqrt(len(y[4])) ]
    plt.yticks(np.arange(0.95, 1.2, 0.01))
    plt.xticks(xscale, x)
    p = plt.errorbar(x, np.mean(y, axis=1), yerr=error, fmt='o')
    plt.xlabel("RG Ratios")
    plt.ylabel("Mean intensity values normalized by the expected RG values")
    plt.grid()
    plt.savefig(OUTPUT_DIR + "/final_ratio_plot.jpg")

def buildOutputDir():
    # Make output dir and save averaged scans as niftis
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(MINC_FILES_DIR) # Clear current outputs except mask output
        shutil.rmtree(NIFTI_FILES_DIR)
        shutil.rmtree(DENOISED_FILES_DIR)
        shutil.rmtree(TRANSFORMS_DIR)
        shutil.rmtree(BIAS_CORRECTED_DIR)
    if not os.path.exists(MASK_FILES_DIR):
        os.makedirs(MASK_FILES_DIR)
    os.makedirs(MINC_FILES_DIR)
    os.makedirs(TRANSFORMS_DIR)
    os.makedirs(BIAS_CORRECTED_DIR)
    rg_dir_list = ["/101", "/90_5", "/80_6", "/71_8", "/64", "/50_8"]
    sorted_dirs_list = [NIFTI_FILES_DIR, DENOISED_FILES_DIR, MINC_FILES_DIR]
    for d in sorted_dirs_list:
        for rg in rg_dir_list:
            os.makedirs(d + rg)


#########
# Main
#########
if(__name__ == '__main__'):
    maskfile = None
    if(len(sys.argv) > 1):
        maskfile = sys.argv[1]
    findRatios(maskfile)
