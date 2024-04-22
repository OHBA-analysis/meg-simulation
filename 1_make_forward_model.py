"""Make a forward model based on a real subject.

"""

import numpy as np

from osl.source_recon import setup_fsl, rhino

setup_fsl("/well/woolrich/projects/software/fsl")

# Input files
fif_file = "data/raw/mf2pt2_sub-CC110037_ses-rest_task-rest_meg_preproc_raw.fif"
smri_file = "data/raw/sub-CC110037_T1w.nii.gz"

# Extract surfaces from sMRI
rhino.compute_surfaces(
    smri_file=smri_file,
    subjects_dir="data",
    subject="simulation",
    include_nose=False,
)

# Save polhemus data
filenames = rhino.get_coreg_filenames("data", "simulation")
rhino.extract_polhemus_from_info(
    fif_file=fif_file,
    headshape_outfile=filenames["polhemus_headshape_file"],
    nasion_outfile=filenames["polhemus_nasion_file"],
    rpa_outfile=filenames["polhemus_rpa_file"],
    lpa_outfile=filenames["polhemus_lpa_file"],
)

# Remove stray headshape points
hs = np.loadtxt(filenames["polhemus_headshape_file"])
nas = np.loadtxt(filenames["polhemus_nasion_file"])
lpa = np.loadtxt(filenames["polhemus_lpa_file"])
rpa = np.loadtxt(filenames["polhemus_rpa_file"])
remove = np.logical_and(hs[1] > max(lpa[1], rpa[1]), hs[2] < nas[2])
hs = hs[:, ~remove]
remove = hs[2] < min(lpa[2], rpa[2]) - 4
hs = hs[:, ~remove]
remove = np.logical_or(hs[0] < lpa[0] - 5, np.logical_or(hs[0] > rpa[0] + 5, hs[1] > nas[1] + 5))
hs = hs[:, ~remove]
np.savetxt(filenames["polhemus_headshape_file"], hs)

# Coregister
rhino.coreg(
    fif_file=fif_file,
    subjects_dir="data",
    subject="simulation",
    use_headshape=True,
    use_nose=False,
)

# Check coregistration
rhino.coreg_display(
    subjects_dir="data",
    subject="simulation",
    plot_type="surf",
    display_outskin=True,
    display_outskin_with_nose=False,
    display_sensors=True,
    display_sensor_oris=True,
    display_fiducials=True,
    display_headshape_pnts=True,
    filename="data/simulation/rhino/coreg.html",
)

# Calculate the forward model
rhino.forward_model(
    subjects_dir="data",
    subject="simulation",
    model="Single Layer",
    gridstep=8,  # mm
)
