# Mask Files

These were created with:
```
flirt -in MNI152_T1_1mm_brain.nii.gz -ref MNI152_T1_1mm_brain.nii.gz -out MNI152_T1_8mm_brain.nii.gz -applyisoxfm 8
```
where `MNI152_T1_1mm_brain.nii.gz` is the standard T1 that comes with FSL.
