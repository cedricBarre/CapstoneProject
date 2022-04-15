# Useful Imports
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt
import csv
import subprocess
import os
import shutil
import sys

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

    # # Set up the scan data list
    # with open('scans.csv', newline='') as scanfile:
    #     reader = csv.DictReader(scanfile)
    #     for row in reader:
    #         # dataRow = [ row['file_name'], float(row['rg_value']), [], [], [] ]
    #         shutil.copy(row['file_name'], NIFTI_FILES_DIR + '/' + row['rg_value'].replace('.', '_'))
    #         data[row['rg_value']] = [ [], [], 0]
    #         # data.append(dataRow)
    
    # if 1:
    #     print("done")
    #     return

    # if(len(data) == 0):
    #     return

    # Extract the array from the nifti file
    # idx = 0
    # for d in data:
    #     img = nb.load(d[0])
    #     data[idx][2] = np.asarray(img.dataobj)
    #     data[idx][3] = img.header
    #     data[idx][4] = img.affine
    #     idx += 1

    # Average out the scans with the same RG values
    # avgData = [ [ 101, np.zeros(data[0][2].shape), 0 ], [ 50.8, np.zeros(data[0][2].shape), 0 ],
    #             [ 64, np.zeros(data[0][2].shape), 0 ], [ 71.8, np.zeros(data[0][2].shape), 0 ],
    #             [ 80.6, np.zeros(data[0][2].shape), 0 ], [ 90.5, np.zeros(data[0][2].shape), 0 ] ]
    
    #  for d in data:
    #     if( d[1] == 101.0 ):
    #         avgData[0][1] = np.add(avgData[0][1], d[2])
    #         avgData[0][2] += 1
    #         # Store latest header and affine for RG
    #         avgData[0][3] = d[3]
    #         avgData[0][4] = d[4]
    #     elif( d[1] == 50.8 ):
    #         avgData[1][1] = np.add(avgData[1][1], d[2])
    #         avgData[1][2] += 1
    #         # Store latest header and affine for RG
    #         avgData[1][3] = d[3]
    #         avgData[1][4] = d[4]
    #     elif( d[1] == 64 ):
    #         avgData[2][1] = np.add(avgData[2][1], d[2])
    #         avgData[2][2] += 1
    #         # Store latest header and affine for RG
    #         avgData[2][3] = d[3]
    #         avgData[2][4] = d[4]
    #     elif( d[1] == 71.8 ):
    #         avgData[3][1] = np.add(avgData[3][1], d[2])
    #         avgData[3][2] += 1
    #         # Store latest header and affine for RG
    #         avgData[3][3] = d[3]
    #         avgData[3][4] = d[4]
    #     elif( d[1] == 80.6 ):
    #         avgData[4][1] = np.add(avgData[4][1], d[2])
    #         avgData[4][2] += 1
    #         # Store latest header and affine for RG
    #         avgData[4][3] = d[3]
    #         avgData[4][4] = d[4]
    #     elif( d[1] == 90.5 ):
    #         avgData[5][1] = np.add(avgData[5][1], d[2])
    #         avgData[5][2] += 1
    #         # Store latest header and affine for RG
    #         avgData[5][3] = d[3]
    #         avgData[5][4] = d[4]

    # Call segmentation script to remove the background of the scan
    # mask_reference_file = os.listdir(NIFTI_FILES_DIR + "/101")[0] # Choose one RG 101 file to be the reference for the mask creation
    # existing_mask = '' if maskfile == None else maskfile # Will bypass mask creation if a mask file is supplied already
    # p = subprocess.Popen("./segmentBrain.sh {} {} {} {}".format(mask_reference_file, MINC_FILES_DIR, OUTPUT_DIR, existing_mask),
    #                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # while(p.poll() is None):
    #     line = p.stdout.readline().decode('utf-8')
    #     if(len(line) != 0):
    #         print(line)

    # Load mask
    mask = np.asarray(nb.load((MASK_FILES_DIR + "/PDw_mask.nii.gz") if maskfile == None else maskfile).dataobj)

    for sorted_dir in os.listdir(DENOISED_FILES_DIR):
        if os.path.isdir(sorted_dir):
            scan_list = os.listdir(sorted_dir)
            scan_amount = len(scan_list)
            rg = os.path.basename(os.path.normpath(sorted_dir)).replace("_", ".")
            datarow = data[rg]
            datarow[0] = np.zeros((scan_amount, mask.shape[0], mask.shape[1], mask.shape[2]))
            datarow[1] = [0] * scan_amount
            idx = 0
            for denoised_scan in scan_list:
                scan_array = np.asarray(nb.load(denoised_scan).dataobj)
                datarow[0][idx, :, :, :] = scan_array
                datarow[1][idx] = np.mean(scan_array[mask.astype(bool)])
            datarow[2] = np.mean(datarow[1][idx])
            data[rg] = datarow


    

    # # Calculate the ratios
    # idx = 0
    # for d in avgData:
    #     avgData[idx][6] = np.mean(d[1][mask.astype(bool)])
    #     idx += 1

    # # Print results
    # print("+------------+------------+------------+------------+------------+\n" +
    #       "|  101/90.5  |  101/80.6  |  101/71.8  |  101/64.0  |  101/50.8  |\n" +
    #       "+------------+------------+------------+------------+------------+\n" +
    #       "|  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |  {:.6f}  |\n".format(
    #                                                                         round((avgData[0][6]/avgData[5][6]), 6),
    #                                                                         round((avgData[0][6]/avgData[4][6]), 6),
    #                                                                         round((avgData[0][6]/avgData[3][6]), 6),
    #                                                                         round((avgData[0][6]/avgData[2][6]), 6),
    #                                                                         round((avgData[0][6]/avgData[1][6]), 6)) +
    #       "+------------+------------+------------+------------+------------+")

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
