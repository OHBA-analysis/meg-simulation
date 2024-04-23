"""Simulate sensor-level data.

"""

import mne
import numpy as np
import colorednoise as cn

from osl.source_recon import setup_fsl
from osl.source_recon.beamforming import get_leadfields
from osl.source_recon.parcellation.parcellation import resample_parcellation

setup_fsl("/well/woolrich/projects/software/fsl")

# Get leadfields in MNI space
leadfields, coords = get_leadfields("data", "simulation", verbose=False)

# Get the parcellation for the coords in MNI space
parcellation = resample_parcellation(
    'data/parcellations/fmri_d100_parcellation_with_PCC_reduced_2mm_ss5mm_ds8mm.nii.gz',
    coords,
)
n_voxels, n_parcels = parcellation.shape

# Binarise the parcellation
for parcel in range(n_parcels):
    thresh = np.percentile(np.abs(parcellation[:, parcel]), 95)
    mapsign = np.sign(np.mean(parcellation[parcellation[:, parcel] > thresh, parcel]))
    scaled_parcellation = mapsign * parcellation[:, parcel] / np.max(np.abs(parcellation[:, parcel]))

voxel_assignments = np.zeros_like(parcellation)
for voxel in range(n_voxels):
    if np.all(parcellation[voxel] == 0):
        continue
    winning_parcel = np.argmax(parcellation[voxel])
    voxel_assignments[voxel, winning_parcel] = 1

# Simulate voxel data
n_samples = 25600
t = np.arange(n_samples) / 250
voxel_data = 1e-12 * cn.powerlaw_psd_gaussian(exponent=1, size=(n_voxels, n_samples))

# Visual activity
for parcel in [0, 1, 2, 3, 24, 25]:
    A = 5e-13 * np.random.uniform(0.8, 1.2)
    f = np.random.uniform(9.97, 10.03)
    phi = np.random.uniform(-0.2 * np.pi, 0.2 * np.pi)
    parcel_mask = voxel_assignments[:, parcel].astype(bool)
    voxel_data[parcel_mask,:] += A * np.sin(2 * np.pi * f * t + phi)

# Motor activity
for parcel in [8, 9, 18, 19]:
    A = 5e-13 * np.random.uniform(0.8, 1.2)
    f = np.random.uniform(19.97, 20.03)
    phi = np.random.uniform(-0.2 * np.pi, 0.2 * np.pi)
    parcel_mask = voxel_assignments[:, parcel].astype(bool)
    voxel_data[parcel_mask,:] += A * np.sin(2 * np.pi * f * t + phi)

# Project to sensors
sensor_data = leadfields @ voxel_data

# Get info for a sensor data fif file
info = mne.io.read_info("data/simulation/rhino/coreg/info-raw.fif")  # contains all channels
dummy_raw = mne.io.RawArray(np.zeros([len(info.ch_names), 1]), info)
dummy_raw = dummy_raw.pick_types(meg=True)
info = dummy_raw.info  # contains MEG channels only

# Save in fif format
raw = mne.io.RawArray(sensor_data, info)
raw.save("data/simulation/sensor-raw.fif", overwrite=True)

# Plot PSD
fig = raw.compute_psd().plot(show=False)
fig.savefig("plots/sensor_psd.png")
