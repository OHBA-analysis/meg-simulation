"""Source reconstruction.

"""

import os

from osl.source_recon import setup_fsl, wrappers

setup_fsl("/well/woolrich/projects/software/fsl")

def run(cmd):
    print(cmd)
    os.system(cmd)

# Copy forward model
run("mkdir -p data/src")
run("cp -r data/simulation/rhino data/src")

# Beamforming
wrappers.beamform(
    src_dir="data",
    subject="src",
    preproc_file="data/simulation/sensor-raw.fif",
    smri_file=None,
    epoch_file=None,
    chantypes=["mag", "grad"],
    rank={"meg": 60},
    freq_range=[1, 45],
)

# Parcellation
wrappers.parcellate(
    src_dir="data",
    subject="src",
    preproc_file="data/simulation/sensor-raw.fif",
    smri_file=None,
    epoch_file=None,
    parcellation_file="fmri_d100_parcellation_with_PCC_reduced_2mm_ss5mm_ds8mm.nii.gz",
    method="spatial_basis",
    orthogonalisation="symmetric",
)
