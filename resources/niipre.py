#!/usr/bin/env python3

# Quick display of a Nifti image

# Packages
import nibabel as nb
import numpy as np
import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Disable Toolbar for plots
plt.rcParams['toolbar'] = 'None'

# Environment and file names
home = str(Path.home())
iFile = sys.argv[1]
oFile = (str(os.path.basename(iFile).replace('.nii.gz', '.png').replace('.nii', '.png')))

# Set rounding
np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})

### IMPORT DATA ###
# Load data
image = nb.load(iFile)

# 3D data
if image.header['dim'][0] == 3:
    data = image.get_data()
    # 4D data
elif image.header['dim'][0] == 4:
    data = image.get_data()[:, :, :, 0]

# Header
header = image.header

# Set NAN to 0
data[np.isnan(data)] = 0

### PREPARE SOME PARAMETERS ###

# Spacing for Aspect Ratio
sX = header['pixdim'][1]
sY = header['pixdim'][2]
sZ = header['pixdim'][3]

# Size per slice
lX = data.shape[0]
lY = data.shape[1]
lZ = data.shape[2]

# Middle slice number
mX = int(lX / 2)
mY = int(lY / 2)
mZ = int(lZ / 2)

# True middle point
tmX = lX / 2.0
tmY = lY / 2.0
tmZ = lZ / 2.0

### ORIENTATION ###
qfX = image.get_qform()[0, 0]
sfX = image.get_sform()[0, 0]

if qfX < 0 and (sfX == 0 or sfX < 0):
    oL = 'R'
    oR = 'L'
elif qfX > 0 and (sfX == 0 or sfX > 0):
    oL = 'L'
    oR = 'R'
if sfX < 0 and (qfX == 0 or qfX < 0):
    oL = 'R'
    oR = 'L'
elif sfX > 0 and (qfX == 0 or qfX > 0):
    oL = 'L'
    oR = 'R'

### PLOTTING ###

# Plot main window
fig = plt.figure(
    facecolor='black',
    figsize=(5, 4),
    dpi=200
)

# Black background
plt.style.use('dark_background')

# Set title
fig.canvas.set_window_title(oFile.replace('.png', ''))

# Coronal
ax1 = fig.add_subplot(2, 2, 1)
imgplot = plt.imshow(
    np.rot90(data[:, mY, :]),
    aspect=sZ / sX,
)
imgplot.set_cmap('gray')

ax1.hlines(tmZ, 0, lX, colors='red', linestyles='dotted', linewidth=.5)
ax1.vlines(tmX, 0, lZ, colors='red', linestyles='dotted', linewidth=.5)

plt.axis('off')

# Sagittal
ax2 = fig.add_subplot(2, 2, 2)
imgplot = plt.imshow(
    np.rot90(data[mX, :, :]),
    aspect=sZ / sY,
)
imgplot.set_cmap('gray')

ax2.hlines(tmZ, 0, lY, colors='red', linestyles='dotted', linewidth=.5)
ax2.vlines(tmY, 0, lZ, colors='red', linestyles='dotted', linewidth=.5)

plt.axis('off')

# Axial
ax3 = fig.add_subplot(2, 2, 3)
imgplot = plt.imshow(
    np.rot90(data[:, :, mZ]),
    aspect=sY / sX
)
imgplot.set_cmap('gray')

ax3.hlines(tmY, 0, lX, colors='red', linestyles='dotted', linewidth=.5)
ax3.vlines(tmX, 0, lY, colors='red', linestyles='dotted', linewidth=.5)

plt.axis('off')

plt.text(-10, mY + 5, oL, fontsize=9, color='red')  # Label on left side

# Textual information
# sform code
sform = np.round(image.get_sform(), decimals=2)
sform_txt = str(sform).replace('[', ' ').replace(']', ' ').replace(' ', '   ').replace('   -', '  -')

# qform code
qform = np.round(image.get_qform(), decimals=2)
qform_txt = str(qform).replace('[', ' ').replace(']', ' ').replace(' ', '   ').replace('   -', '  -')

# Dimensions
dims = str(data.shape).replace(', ', ' x ').replace('(', '').replace(')', '')
dim = ("Dimensions: " + dims)

# Spacing
spacing = ("Spacing: "
           + str(np.round(sX, decimals=2))
           + " x "
           + str(np.round(sY, decimals=2))
           + " x "
           + str(np.round(sZ, decimals=2))
           + " mm"
           )

# Data type
type = image.header.get_data_dtype()
type_str = ("Data type: " + str(type))

# Volumes
volumes = ("Volumes: " + str(image.header['dim'][4]))

# Range
min = np.round(np.amin(data), decimals=2)
max = np.round(np.amax(data), decimals=2)
range = ("Range: " + str(min) + " - " + str(max))

text = (
        dim + "\n"
        + spacing + "\n"
        + volumes + "\n"
        + type_str + "\n"
        + range + "\n\n"
        + "sform code:\n"
        + sform_txt + "\n"
        + "\nqform code:\n"
        + qform_txt
)

# Plot text subplot
ax4 = fig.add_subplot(2, 2, 4)
plt.text(
    0.15,
    0.95,
    text,
    horizontalalignment='left',
    verticalalignment='top',
    size=6,
    color='white',
)
plt.axis('off')

# Adjust whitespace
plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

# Display
# plt.show()

plt.savefig(sys.stdout.buffer, dpi=120)