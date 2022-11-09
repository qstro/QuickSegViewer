# QuickSegViewer
Small Python script to quickly visually verify large amounts of medical image segmentation data


# Usage
- 'data' folder containing subfolders 'img' (image data) and 'mask' (segmentation masks) and patients.txt (list of case IDs, one per line)
- filenames start with case ID, image files end with 0000 - 0003 depending on sequence (e.g. in MRI image data)
- image and mask files are in .nii.gz format

run quicksegviewer.py

Sceenshot:
![Alt text](QuickSegViewer_example.png?raw=true "Screenshot")
