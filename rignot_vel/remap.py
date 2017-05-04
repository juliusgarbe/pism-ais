
"""
matthias.mengel@pik, torsten.albrecht@pik
Regridding: bring your data to the grid we commonly use for PISM Antarctica
simulations. This is equivalent to the ALBMAP grid.
This step will take a while if high resolution data is processed.
Regrid Velocity data to various grid resolution using cdo remapcony.

"""

import os, sys
import jinja2

## this hack is needed to import config.py from the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path: sys.path.append(project_root)
import config as cf; reload(cf)
import pism_input.pism_input as pi; reload(pi)

dataset="rignotvel"
# resolution for the output file, set from config.
resolution = cf.resolution # in km
# conservative regridding for bedmap2, albmap and velocity data. does
# not yet work for the other datasets.
use_conservative_regridding = True

data_path = os.path.join(cf.output_data_path, dataset)
inputfile = os.path.join(data_path, 'rignotvel_450m_input.nc')
regridded_file = os.path.join(data_path, dataset+"_"+str(resolution)+"km.nc")

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

pi.write_regrid_submission_file(cf, data_path, dataset, inputfile, resolution,
                                cdo_targetgrid_file, regridded_file, use_conservative_regridding)
