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

def presentAnalysis(input_folder : str, output_folder : str):
    print(f"    - Looking for drift parameters starting at folder: {input_folder}")
    print(f"    - Output folder: {output_folder}")

    combined_scan_params = os.path.join(output_folder, "combined_bold_scan_params.csv")
    scan_params_fieldnames = ['Subject ID', 'Pixel Volume (mm^3)', 'Repetition Time (s)', 'Echo Time (s)', 
                                'Drift Rotation X', 'Drift Rotation Y', 'Drift Rotation Z',
                                'Drift Translation X', 'Drift Translation Y', 'Drift Translation Z', 
                                'Drift Framewise', 'Framewise Displacement STD', 'Mean of STD Difference', 
                                'Algorithm Version', 'Dataset' ]

    all_drift_files = glob.glob(os.path.join(input_folder, "**/analysis_data.csv"), recursive=True)
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
    longer_df_rot = pd.wide_to_long(df.reset_index(), stubnames=['Drift Rotation'], 
                                i='index', j='Drift Rotation Axis', suffix="\\D+")

    longer_df_tran = pd.wide_to_long(df.reset_index(), stubnames=['Drift Translation'], 
                                i='index', j='Drift Translation Axis', suffix="\\D+")
    
    colors = {"rabies_7_Cryo_aw_f": "red",
             "rabies_7_Cryo_med_f1": "blue",
             "rabies_7_Cryo_med_f2": "green",
             "rabies_7_RT_halo_v": "black",
             "rabies_7_RT_med_f": "orange",
             "rabies_94_RT_iso_v": "purple"}
    drift_relavent_datasets = ["rabies_7_Cryo_med_f1",
                                "rabies_7_Cryo_med_f2"]
    control_dataset = "rabies_94_RT_iso_v"
    fake_high_motion_dataset = "rabies_7_RT_halo_v"
    real_motion_dataset = "rabies_7_Cryo_aw_f"

    rot_versions = longer_df_rot.groupby('Algorithm Version')
    tran_versions = longer_df_tran.groupby('Algorithm Version')
    versions = df.groupby('Algorithm Version')

    # Drift plot
    for version in ['old', 'new']:
        fig,axes = plt.subplots(nrows=2, ncols=3, figsize=(20,5))
        version_obj = []
        if version in rot_versions.groups.keys():
            rot_by_dataset = rot_versions.get_group(version).groupby('Dataset')
            version_obj.append([rot_by_dataset, 'Rotation'])
        if version in tran_versions.groups.keys():
            tran_by_dataset = tran_versions.get_group(version).groupby('Dataset')
            version_obj.append([tran_by_dataset, 'Translation'])
        for i, param in enumerate(version_obj):
            plot_pixvol = axes[i,0]
            plot_pixvol.plot(param[0].get_group('rabies_7_Cryo_med_f1')['Pixel Volume (mm^3)'],
                            param[0].get_group('rabies_7_Cryo_med_f1')[f'Drift {param[1]}'], 
                            'o', label='rabies_7_Cryo_med_f1')
            plot_pixvol.plot(param[0].get_group('rabies_7_Cryo_med_f2')['Pixel Volume (mm^3)'],
                            param[0].get_group('rabies_7_Cryo_med_f2')[f'Drift {param[1]}'], 
                            'o', label='rabies_7_Cryo_med_f2')
            plot_pixvol.legend()
            plot_pixvol.set_title(f'Estimated {param[1]} drift according to pixel volume', fontsize=10, color='black')
            plot_pixvol.set_xlabel('Pixel Volume (mm^3)')
            plot_pixvol.set_ylabel(f'{param[1]} Drift Magnitude')
            plot_rep_time = axes[i,1]
            plot_rep_time.plot(param[0].get_group('rabies_7_Cryo_med_f1')['Repetition Time (s)'],
                            param[0].get_group('rabies_7_Cryo_med_f1')[f'Drift {param[1]}'], 
                            'o', label='rabies_7_Cryo_med_f1')
            plot_rep_time.plot(param[0].get_group('rabies_7_Cryo_med_f2')['Repetition Time (s)'],
                            param[0].get_group('rabies_7_Cryo_med_f2')[f'Drift {param[1]}'], 
                            'o', label='rabies_7_Cryo_med_f2')
            plot_rep_time.legend()
            plot_rep_time.set_title(f'Estimated {param[1]} drift according to repetition time', fontsize=10, color='black')
            plot_rep_time.set_xlabel('Repetition Time (s)')
            plot_rep_time.set_ylabel(f'{param[1]} Drift Magnitude')
            plot_echo_time = axes[i,2]
            plot_echo_time.plot(param[0].get_group('rabies_7_Cryo_med_f1')['Echo Time (s)'],
                            param[0].get_group('rabies_7_Cryo_med_f1')[f'Drift {param[1]}'], 
                            'o', label='rabies_7_Cryo_med_f1')
            plot_echo_time.plot(param[0].get_group('rabies_7_Cryo_med_f2')['Echo Time (s)'],
                            param[0].get_group('rabies_7_Cryo_med_f2')[f'Drift {param[1]}'], 
                            'o', label='rabies_7_Cryo_med_f2')
            plot_echo_time.legend()
            plot_echo_time.set_title(f'Estimated {param[1]} drift according to echo time', fontsize=10, color='black')
            plot_echo_time.set_xlabel('Echo Time (s)')
            plot_echo_time.set_ylabel(f'{param[1]} Drift Magnitude')
        fig.tight_layout()
        fig.savefig(os.path.join(output_folder, f"drift_plots_{version}_ants.png"))
    
    # Framewise displacement drift according to version
    fig,axes = plt.subplots(nrows=1, ncols=2, figsize=(20,5))
    drift_data = df[df['Dataset'].isin(drift_relavent_datasets)]
    drift_grouped = drift_data.groupby('Algorithm Version')
    version_data = []
    version_name = []
    for name, version in drift_grouped:
        version_data.append(version['Drift Framewise'])
        version_name.append(name)
    p = axes[0]
    for data in version_data:
        p.hist(data, bins=30)
    p.set_title(f'Distribution of framewise displacement across subjects according to the ANTs version', fontsize=15, color='black')
    p.set_xlabel('Framewise displacement drift')
    p.set_ylabel('Count')
    p.legend(version_name)
    p = axes[1]
    p.boxplot(version_data)
    p.set_xticklabels(version_name)
    p.set_title('Boxplot of framewise displacement across subjects according to the ANTs version', fontsize=15, color='black')
    p.set_ylabel('Framewise displacement drift')
    p.set_xlabel('ANTs version')
    fig.tight_layout()
    fig.savefig(os.path.join(output_folder, "drift_comparison.png"))

    # Real motion dataset
    fig,axes = plt.subplots(nrows=1, ncols=2, figsize=(20,5))
    rm_data = df[(df['Dataset'] == real_motion_dataset)]
    rm_grouped = rm_data.groupby('Algorithm Version')
    version_data = []
    version_name = []
    for name, version in rm_grouped:
        version_data.append(version['Mean of STD Difference'])
        version_name.append(name)
    p = axes[0]
    for data in version_data:
        p.hist(data, bins=30)
    p.set_title(f'Distribution of the mean for the difference in STD between pre and post correction\nscans across subjects according to the ANTs version', fontsize=15, color='black')
    p.set_xlabel('Mean for the difference in STD')
    p.set_ylabel('Count')
    p.legend(version_name)
    p = axes[1]
    p.boxplot(version_data)
    p.set_xticklabels(version_name)
    p.set_title('Boxplot of the mean for the difference in STD between pre and post correction\nscans across subjects according to the ANTs version', fontsize=15, color='black')
    p.set_ylabel('Mean for the difference in STD')
    p.set_xlabel('ANTs version')
    fig.tight_layout()
    fig.savefig(os.path.join(output_folder, "real_motion_comparison.png"))

    # Fake high motion dataset
    fig,axes = plt.subplots(nrows=1, ncols=2, figsize=(20,5))
    fhm_data = df[(df['Dataset'] == fake_high_motion_dataset)]
    fhm_grouped = fhm_data.groupby('Algorithm Version')
    version_data = []
    version_name = []
    for name, version in fhm_grouped:
        version_data.append(version['Framewise Displacement STD'])
        version_name.append(name)
    p = axes[0]
    for data in version_data:
        p.hist(data, bins=30)
    p.set_title(f'Distribution of framewise displacement spread across subjects according to the ANTs version', fontsize=15, color='black')
    p.set_xlabel('Framewise displacement spread')
    p.set_ylabel('Count')
    p.legend(version_name)
    p = axes[1]
    p.boxplot(version_data)
    p.set_xticklabels(version_name)
    p.set_title('Boxplot of framewise displacement spread across subjects according to the ANTs version', fontsize=15, color='black')
    p.set_ylabel('Framewise displacement spread')
    p.set_xlabel('ANTs version')
    fig.tight_layout()
    fig.savefig(os.path.join(output_folder, "fake_high_motion_comparison.png"))

if __name__ == "__main__":
    print("Assembling the analysis conducted on a variety of subjects")
    args = parseArguments()

    presentAnalysis(args.input_folder, args.output_folder)