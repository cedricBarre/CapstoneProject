import csv, argparse, glob, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def parseArguments():
    parser = argparse.ArgumentParser(description='Head motion correction stage of RABIES pipeline preprocessing stage', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_folder', 
                        help="Input folder which contains the datasets from which the drift parameters will be extracted\n"
                                " from each subjects")
    parser.add_argument('output_folder', 
                        help='Output folder')

    return parser.parse_args()

def presentDriftAnalysis(input_folder : str, output_folder : str):
    print(f"    - Looking for drift parameters starting at folder: {input_folder}")
    print(f"    - Output folder: {output_folder}")

    combined_scan_params = os.path.join(output_folder, "combined_bold_scan_params.csv")
    drift_plots = os.path.join(output_folder, "drift_plots.png")
    scan_params_fieldnames = ['Subject ID', 'Pixel Volume (mm^3)', 'Repetition Time (s)', 'Echo Time (s)', 
                                'Drift X Rotation', 'Drift Y Rotation', 'Drift Z Rotation',
                                'Drift X Translation', 'Drift Y Translation', 'Drift Z Translation', 
                                'Dataset' ]


    all_drift_files = glob.glob(os.path.join(input_folder, "**/bold_scan_params.csv"), recursive=True)
    with open(combined_scan_params, 'w') as combined_scan_params_fp:
        combined_scan_params_w = csv.writer(combined_scan_params_fp, delimiter=',', quotechar='|')
        combined_scan_params_w.writerow(scan_params_fieldnames)
        for drift_file in all_drift_files:
            with  open(drift_file, 'r') as drift_file_fp:
                drift_file_r   = csv.reader(drift_file_fp, delimiter=',', quotechar='|')
                dataset = drift_file.split('/')[-4]
                for i, row in enumerate(drift_file_r):
                    if (i == 1):
                        combined_scan_params_w.writerow(np.hstack([row, [dataset]]))
    
    df = pd.read_csv(combined_scan_params)
    longer_df = pd.wide_to_long(df, stubnames=['Drift'], 
                                i='Subject ID', j='Drift Type', suffix="\\D+")
    groups = longer_df.groupby('Dataset')
    
    colors = {"rabies_7_Cryo_aw_f": "red",
             "rabies_7_Cryo_med_f1": "blue",
             "rabies_7_Cryo_med_f2": "green",
             "rabies_7_RT_halo_v": "black",
             "rabies_7_RT_med_f": "orange",
             "rabies_94_Cryo_mediso_v": "purple"}

    fig,axes = plt.subplots(nrows=1, ncols=3, figsize=(20,5))
    plot_pixvol = axes[0]
    for name, group in groups:
        plot_pixvol.plot(group['Pixel Volume (mm^3)'], group['Drift'], 'o', label=name)
    plot_pixvol.legend()
    plot_pixvol.set_title('Estimated drift according to pixel volume', fontsize=15, color='black')
    plot_pixvol.set_xlabel('Pixel Volume (mm^3)')
    plot_pixvol.set_ylabel('Drift Magnitude')
    plot_rep_time = axes[1]
    for name, group in groups:
        plot_rep_time.plot(group['Repetition Time (s)'], group['Drift'], 'o', label=name)
    plot_rep_time.legend()
    plot_rep_time.set_title('Estimated drift according to repetition time', fontsize=15, color='black')
    plot_rep_time.set_xlabel('Repetition Time (s)')
    plot_rep_time.set_ylabel('Drift Magnitude')
    plot_echo_time = axes[2]
    for name, group in groups:
        plot_echo_time.plot(group['Echo Time (s)'], group['Drift'], 'o', label=name)
    plot_echo_time.legend()
    plot_echo_time.set_title('Estimated drift according to echo time', fontsize=15, color='black')
    plot_echo_time.set_xlabel('Echo Time (s)')
    plot_echo_time.set_ylabel('Drift Magnitude')
    
    fig.savefig(drift_plots)

if __name__ == "__main__":
    print("Assembling the drift analysis conducted on a variety of subjects")
    args = parseArguments()

    presentDriftAnalysis(args.input_folder, args.output_folder)