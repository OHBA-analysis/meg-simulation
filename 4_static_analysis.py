"""Static network analysis.

"""

import os

from osl_dynamics.data import Data
from osl_dynamics.analysis import static, power, connectivity

os.makedirs("plots", exist_ok=True)

mask_file = "MNI152_T1_8mm_brain.nii.gz"
parcellation_file = "fmri_d100_parcellation_with_PCC_reduced_2mm_ss5mm_ds8mm.nii.gz"

# Load data
data = Data("data/src/parc/parc-raw.fif")
x = data.time_series()

# Calculate multitaper spectra
f, psd, coh = static.multitaper_spectra(
    data=x,
    sampling_frequency=250,
    calc_coh=True,
)

# Calculate power maps and plot
power_maps = [
    power.variance_from_spectra(f, psd, frequency_range=[9, 11]),
    power.variance_from_spectra(f, psd, frequency_range=[19, 21]),
]
power.save(
    power_maps,
    mask_file=mask_file,
    parcellation_file=parcellation_file,
    plot_kwargs={"symmetric_cbar": True},
    filename="plots/static_pow_.png"
)

# Calculate coherence networks and plot
conn_maps = [
    connectivity.mean_coherence_from_spectra(f, coh, frequency_range=[9, 11]),
    connectivity.mean_coherence_from_spectra(f, coh, frequency_range=[19, 21]),
]
connectivity.save(
    conn_maps,
    parcellation_file=parcellation_file,
    threshold=0.98,
    filename="plots/static_coh_.png",
)

# Delete temporary directory
data.delete_dir()
