# Head Motion Correction Performance Evaluation

This project holds the automation software to evaluate the performance of the head motion correction algorithm from the ANTs processing toolkit. A motion visualization tool is also included which allows users to create short video clips that animate the motion of the brain in a fMRI timeseries. 

## Setting Up the Anaconda Environment

In order to run the head motion correction processing script, the analysis script and the visualization generation script on the CIC, an Anaconda environment must be created with the help of the [hmc_env.yml](hmc_env.yml) file in this directory. To create the environment, execute the following lines of code in a terminal within the directory holding the [hmc_env.yml](hmc_env.yml) file.

```
module load anaconda
conda env create -f hmc_env.yml
```

The second line of code might take a long time to execute since the environment requires large packages to be installed. If you already have an Anaconda environment with the following packages installed in it, your environment could be used instead:

* Python 3.6
* Numpy
* Matplotlib
* Nibabel
* SimpleITK 

To load the Anaconda environment, execute the following lines of code.

```
module load anaconda # If not already executed before when creating
conda activate hmc_env
```

You are now ready to run the processing scripts on the CIC! If you are running on the singularity of docker, you do not have to create this environment since all the required packages are already installed within the RABIES container.

## Running the Isolated Head Motion Correction

The [run_hmc.sh](run_hmc.sh) script was created for users to be able to execute the head motion correction algorithm from the ANTs software toolkit in isolation and provide some quality control similar to what is done in the RABIES pipeline. The processing also includes the analysis of the 3 main motion types of interest for our project: real motion, drift motion and high unrealistic motion. The script characterizes the presence of these types motions in each scan it processes and stores the results in a CSV file in the output folder. This information can then be used by a subsequent analysis script ([combined_analysis.py](combined_analysis.py)) which can collect all the output data files from all the scans processed within a directory and create relevant plots to compare the performance of two different ANTs toolkit versions. Let us start with the description of how to use the processing script.

### Head Motion Correction Processing Script

To run the head motion correction processing script [run_hmc.sh](run_hmc.sh), the user must specify a few required command line arguments and options. The following table describes the different options and arguments to supply to the script on the command line.

| Argument            | Type     | Value                      |
|---------------------|----------|----------------------------|
| -i or --input       | Required | Relative or absolute path to the folder containing the input data. |
| -o or --output      | Required | Relative or absolute path to the folder into which the output data will be stored. |
| -d or --dataset     | Optional | No value required. Specifying this option on the command line tells the script that a full dataset will be processed. Omiting this option tells the script that a single subject will be processed. |
| -p or --performance | Optional | No value required. Specifying this option on the command line tells the script to use the fast head motion correction. Omiting this option tells the script to use a slower head motion correction. This option is only effective when running on the CIC with the latest version. Execution in singularity or with the older version is fast by default. |
| -b or --batch       | Optional | No value required. Specifying this option on the command line tells the script to use the batching system on the CIC to batch the head motion correction of the subjects inside the dataset. Using this option for a single subject will still work but no substantial speed up will be achieved. This option is only available when running on the CIC. |
| -l or --latest | Optional | No value required. Specifying this option on the command line tells the script to use the latest version of the ANTs toolkit (2.4.0) for head motion correction. Omiting this option will tell the script to use the older version (2.3.1). This option is only available when running on the CIC. Make sure to choose the right machine to run the desired version since some CIC machines have ANTs 2.3.1 and other have ANTs 2.4.0. |
| -c or --containerized | Optional | Relative or absolute path to the RABIES singularity image. This will instruct the script to run inside the RABIES container. |
| -s | Optional | Name of the subfolder into which the output data will be stored for each subject in the output folder. This is useful when you want to have many runs of head motion correction with different configurations and not have each run overwrite previous runs inside the same output folder. When running a single subject, do not use this option. Instead, include the subfolder directly in the output path. |

Running the help command on the command line can also be helpful:

```
./run_hmc.sh -h
```

The [test_data](test_data/) folder included in this repository provides two compressed folders that serve as examples of the input folder structure since the script relies on a specific input folder structure similar to the one used in BIDS. The [test_subject.tar.gz](test_data/test_subject.tar.xz) holds the folder structure with an example of a single subject and the [test_dataset.tar.gz](test_data/test_dataset.tar.xz) holds the folder structure with an example of a dataset. These compressed files can be extracted anywhere the user sees fit. 

For a single subject, the input folder structure must agree with the following template:

```
sub-0XX
   └── ses-1
        └── func
            ├── _scan_info_subject_id0XX.session1.runNone_split_name_sub-0XX_ses-1_task-rest_acq-EPI_bold
            │   └── sub-0XX_ses-1_task-rest_acq-EPI_bold_bold_ref.nii.gz
            ├── sub-0XX_ses-1_func_sub-0XX_ses-1_task-rest_acq-EPI_bold.json
            └── sub-0XX_ses-1_task-rest_acq-EPI_bold.nii.gz
```

Here, XX represents the unique identifier number of the subject. For a dataset, the input folder structure should agree with the following template:

```
dataset1
    ├── sub-00A
    ├── sub-00B
    ├── sub-00C
    ...
    └── sub-ZZZ
```

Each of the _sub-XXX_ subfolders are individual subject folders that agree with the subject folder structure mentionned above. 

The output folder will be created by the script if it does not already exist. When running the processing of many different datasets, we suggest storing all dataset output folder within the same folder as follows:

```
all_outputs
    ├── dataset1_output
    |       ├── sub-00A
    |       ...
    |       └── sub-ZZZ
    ├── dataset2_output
    |       ├── sub-00A
    |       ...
    |       └── sub-ZZZ
    ├── dataset3_output
    |       ├── sub-00A
    |       ...
    |       └── sub-ZZZ
    ...
    └── datasetX_output
            ├── sub-00A
            ...
            └── sub-ZZZ
```

Here are a few command examples on how to run the script. Note that the script should be executed inside the anaconda environment if running on the CIC.

* Running script on CIC for single subject

```
./run_hmc.sh -i <path to input folder>/ -o <path to output folder>/ 
```
* Running script on CIC for dataset with subfolder specified

```
./run_hmc.sh -i <path to input folder>/ -o <path to output folder>/ -d -s <subfolder name>
```
* Running script on singularity for dataset with subfolder specified

```
./run_hmc.sh -i <path to input folder>/ -o <path to output folder>/ -d -s <subfolder name> -c <path to rabies .sif image>
```

* Running script on CIC for dataset with subfolder specified, batch, performance and latest version enabled

```
./run_hmc.sh -i <path to input folder>/ -o <path to output folder>/ -d -b -p -l -s <subfolder name>
```

### Head Motion Correction Analysis

Once many datasets have been processed for both the new and old version of the algorithm and the results stored as intructed above, the analysis script can be executed to collect all the data into intuitive plots. This script will create plots that will allow the user to compare the performance of the two different ANTs toolkit version for the head motion correction based of the estimation of drift motion, high unrealistic motion and real motion. To run the analysis script run the following command within the anaconda environments:

```
python combined_analysis.py <path to the input folder> <path to the output folder>
```

The script only takes in two required arguments: the input folder and the output folder. The input folder corresponds to the output folder of the previous head motion correction processing with all the dataset output subfolders. The output folder corresponds to the folder where all the output plots of the analysis will be stored. This latter folder must already exist to run the analysis. The user can consult the help command of the script if necessary:

```
python combined_analysis.py -h
```

## Running the Visualization Tool

The [animation.py script](animation.py) was created for users to be able to create an animation of different fMRI. Having access to these animation is quite important to be able to distinguish real and fake head motion. The script animates 4 slices for each of the 3 views of the scans for 3 to 4 seconds.

### Head Motion Correction Processing Script

To run the visualisation tool processing script [animation.py], the user must specify the input folder, the otuput folder and one optional command line argument. The optional command line argument is describe below

| Argument            | Type     | Value                      |
|---------------------|----------|----------------------------|
| -i or --input       | Required | Relative or absolute path to the folder containing the input data. |
| -o or --output      | Required | Relative or absolute path to the folder into which the output data will be stored. |
| -d or --dataset     | Optional | No value required. Specifying this option on the command line tells the script that a full dataset will be processed. Omiting this option tells the script that a single subject will be processed. |

The file structure should follow the framework described above for the "Head Motion Correction Processing Script". Here are two exemples on how to run the script.

* Running script on CIC for single subject

```
python3 ./animation.py <input-file> <output-file> 
```

```
python3 ./animation.py <input-file> <output-file> -d
```

