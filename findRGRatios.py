# Useful Imports
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt
import csv
import subprocess
import os
import shutil

# Global variable declaration
OUTPUT_DIR = "output/"
MINC_FILES_DIR = "output/minc_files"
NIFTI_FILES_DIR = "output/nifti_files"
MASK_FILES_DIR = "output/masks"

def findRatios():
    data = []

    # Set up the scan data list
    with open('scans.csv', newline='') as scanfile:
        reader = csv.DictReader(scanfile)
        for row in reader:
            dataRow = [ row['file_name'], float(row['rg_value']), [], [], [] ]
            data.append(dataRow)
    
    if(len(data) == 0):
        return
    
    # Extract the array from the nifti file
    idx = 0
    for d in data:
        img = nb.load(d[0])
        data[idx][2] = np.asarray(img.dataobj)
        data[idx][3] = img.header
        data[idx][4] = img.affine
        idx += 1
    
    # Average out the scans with the same RG values
    avgData = [ [ 101, np.zeros(data[0][2].shape), 0, [], [], [], 0 ], [ 50.8, np.zeros(data[0][2].shape), 0, [], [], [], 0 ] ]
        # Can add more elements to the array for the other possible RG gain values that we encounter
    for d in data:
        if( d[1] == 101.0 ):
            avgData[0][1] = np.add(avgData[0][1], d[2])
            avgData[0][2] += 1
            # Store latest header and affine for RG
            avgData[0][3] = d[3]
            avgData[0][4] = d[4]
        elif( d[1] == 50.8 ):
            avgData[1][1] = np.add(avgData[1][1], d[2])
            avgData[1][2] += 1
            # Store latest header and affine for RG
            avgData[1][3] = d[3]
            avgData[1][4] = d[4]
        
    idx = 0
    for rg in avgData:
        avgData[idx][1] = rg[1]/rg[2]
        idx += 1

    # Make output dir and save averaged scans as niftis
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR) # Clear current outputs
    os.makedirs(MINC_FILES_DIR)
    os.makedirs(NIFTI_FILES_DIR)
    for d in avgData:
        scan = nb.Nifti1Image(d[1], affine=d[4], header=d[3])
        nb.save(scan, os.path.join(NIFTI_FILES_DIR, "PDw_RG_{}.nii.gz".format(str(d[0]).replace('.', '_'))))

    # Call segmentation script to remove the background of the scan
    p = subprocess.Popen("./segmentBrain.sh {} {} {}".format(NIFTI_FILES_DIR, MINC_FILES_DIR, OUTPUT_DIR), 
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(p.poll() is None):
        line = p.stdout.readline().decode('utf-8')
        if(len(line) != 0):
            print(line)
    
    # Load newly created masks for each 
    for file in os.listdir(MASK_FILES_DIR):
        if(file.find("101") > 0):
            avgData[0][5] = np.asarray(nb.load("output/masks/{}".format(file)).dataobj)
        elif(file.find("50_8") > 0):
            avgData[1][5] = np.asarray(nb.load("output/masks/{}".format(file)).dataobj)
        else:
            print("Failed to identify the RG of this mask file: {}".format(file))
    
    # Calculate the ratios
    idx = 0
    for d in avgData:
        avgData[idx][6] = np.mean(np.multiply(d[1], d[5]))
        idx += 1
    
    # Print results
    print("+------------+------------+------------+------------+------------+\n" +
          "|  101/90.5  |  101/80.6  |  101/71.8  |  101/64.0  |  101/50.8  |\n" +
          "+------------+------------+------------+------------+------------+\n" +
          "|    {}     |    {}     |    {}     |    {}     |  {:.8f}  |\n".format(
                                                                            "N/A",
                                                                            "N/A",
                                                                            "N/A",
                                                                            "N/A",
                                                                            round((avgData[0][6]/avgData[1][6]), 8)) +
          "+------------+------------+------------+------------+------------+")
    


#########
# Main
#########
if(__name__ == '__main__'):
    findRatios()