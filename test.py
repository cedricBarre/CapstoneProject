import os
import shutil

MINC_FILES_DIR = "output/minc_files"

if not os.path.exists(MINC_FILES_DIR):
    os.makedirs(MINC_FILES_DIR)
shutil.copy('scans.csv', MINC_FILES_DIR + "/101/")