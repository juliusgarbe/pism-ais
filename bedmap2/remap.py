
"""
matthias.mengel@pik, torsten.albrecht@pik
Regridding: bring your data to the grid we commonly use for PISM Antarctica
simulations. This is equivalent to the ALBMAP grid.
This step will take a while if high resolution data is processed.
Regrid Bedmap2 data to various grid resolution using cdo remapcony.

"""

import os, sys
import jinja2

## this hack is needed to import config.py from the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path: sys.path.append(project_root)
import config as cf; reload(cf)
import pism_input.pism_input as pi; reload(pi)

dataset="bedmap2"
# resolution for the output file
resolution = 50 # in km
data_path = os.path.join(cf.output_data_path, dataset)

# prepare the input file for cdo remapping
# this step takes a while for high resolution data (i.e. 1km)
inputfile = os.path.join(data_path, 'bedmap2_1km_input.nc')
pi.prepare_ncfile_for_cdo(inputfile)

# check if target grid is present.
# the cdo target grids are independent of the specific input dataset.
# they are therefore created beforehand by grids/create_cdo_grid.py
cdo_targetgrid_file = os.path.join(cf.cdo_remapgridpath,'pism_'+str(int(resolution))+'km.nc')

if not os.path.isfile(cdo_targetgrid_file):
    print "cdo target grid file", cdo_targetgrid_file," does not exist."
    print "run grids/create_cdo_grid.py first."
    sys.exit(0)

# Regridding is generally a CPU-heavy task. We therefore do not regrid interactively,
# but prepare a script that can be submitted to compute-clusters. The example is specific
# for PIK's cluster using SLURM.
# use 'sbatch cdo_remap.sh' to submit your job.
# Conservative regridding does not work for all datasets yet, use it for bedmap2 or albmap.
# We use cdo, see https://code.zmaw.de/projects/cdo/embedded/index.html

# make jinja aware of templates in the pism_input/tools folder
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
            searchpath=os.path.join(cf.project_root,"tools")))

scen_template_file = "GENERATED_SCENARIO.SCEN.template"
scen_template = jinja_env.get_template("cdo_remap.sh.template")

regridded_file = os.path.join(data_path, dataset+"_"+str(resolution)+"km.nc")
mapweights = os.path.join(data_path, "mapweights.nc")
use_conservative_regridding = True

out = scen_template.render(user=cf.username,
                           use_conservative_regridding = use_conservative_regridding,
                           targetgrid = cdo_targetgrid_file,
                           inputfile = inputfile,
                           mapweights = mapweights,
                           regridded_file = regridded_file,
                          )

with open("cdo_remap.sh", 'w') as f:
    f.write(out)
print "Wrote cdo_remap.sh, submit with sbatch cdo_remap.sh to compute nodes."