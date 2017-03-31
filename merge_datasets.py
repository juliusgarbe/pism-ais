import os
import subprocess
import config as cf; reload(cf)
import pism_input.pism_input as pi; reload(pi)

datasets_to_merge = ["bedmap2", "albmap"]
resolution = 5 # in km
variables = {"bedmap2":["thk","topg"],
             "albmap":["precipitation","air_temp"]}

# will hold the merged files
data_path = os.path.join(cf.output_data_path, "merged")

merged_filename = ("_").join(datasets_to_merge)+"_"+str(resolution)+"km.nc"
merged_filename = os.path.join(data_path,merged_filename)

if not os.path.exists(data_path): os.makedirs(data_path)

preselected_datapaths = []

added_lat_lon_mapping = False

for ds in datasets_to_merge:

    input_datapath = pi.get_path_to_data(cf.output_data_path,ds,resolution)
    # data with selected variables will be written to /merged directory
    preselected_datapath = pi.get_path_to_data(cf.output_data_path,ds,resolution,
                                data_path)
    selected_variables = ",".join(variables[ds])

    # assume latitude and longitude are present in first input file.
    # TODO: include mapping variable, need to ensure that it is present
    # in all input files first.
    if not added_lat_lon_mapping:
        selected_variables += ",lon,lat"
        added_lat_lon_mapping = True

    cmd = ("ncks -O -4 -v "+selected_variables+" "+
            input_datapath+" "+preselected_datapath)
    print cmd
    subprocess.check_call(cmd,shell=True)
    preselected_datapaths.append(preselected_datapath)

cmd = "cdo -O merge "+" ".join(preselected_datapaths)+" "+merged_filename
print cmd
# if you see "cdo: error while loading shared libraries:",
# 'module load cdo'
subprocess.check_call(cmd,shell=True)