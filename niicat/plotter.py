import io
import importlib
import nibabel as nb
import numpy as np
import matplotlib.pyplot as plt


def try_import(module):
    "Try to import `module`. Returns module's object on success, None on failure"
    try: return importlib.import_module(module)
    except: return None

libsixel = try_import("libsixel")


def _sixel_encode(data, width, height):
    """Adapted from https://github.com/fastai/fastai/blob/master/fastai/sixel.py"""
    s = io.BytesIO()
    output = libsixel.sixel_output_new(lambda data, s: s.write(data), s)
    dither = libsixel.sixel_dither_new(256)
    w,h = int(width),int(height)
    libsixel.sixel_dither_initialize(dither, data, w, h, libsixel.SIXEL_PIXELFORMAT_RGBA8888)
    libsixel.sixel_encode(data, w, h, 1, dither, output)
    return s.getvalue().decode('ascii')


def _plot_sixel(fig=None):
    """Adapted from https://github.com/fastai/fastai/blob/master/fastai/sixel.py"""
    if not libsixel:
        print("`libsixel-python` is missing. See https://github.com/saitoha/libsixel")
        return
    if fig is None: fig = plt.gcf()
    fig.canvas.draw()
    dpi = fig.get_dpi()
    res = _sixel_encode(fig.canvas.buffer_rgba(), fig.get_figwidth()* dpi, fig.get_figheight() * dpi)
    print(res)


def _plot_nifti_preview(iFile, return_fig=False, dpi=150, slice_num=None):
    """Adapted from https://github.com/vnckppl/niipre"""

    # Disable Toolbar for plots
    plt.rcParams['toolbar'] = 'None'

    # Environment and file names
    # iFile = sys.argv[1]

    # Set rounding
    np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})

    # Load data
    image = nb.load(iFile)
    
    # Handle RGB data differently
    if image.header.get_data_dtype().fields is not None:  # Check if structured dtype (RGB)
        data = np.array(image.dataobj)  # Load raw data
        # Convert structured RGB data back to regular array
        from numpy.lib import recfunctions as rfn
        data = rfn.structured_to_unstructured(data)
        # If 4D with RGB, reshape to 3D
        if len(data.shape) == 4:
            data = data[:, :, :, 0]  # Take first RGB component for preview
    else:
        # Regular scalar data
        data = image.get_fdata()
        if image.header['dim'][0] == 4:  # 4D data
            data = data[:, :, :, 0]  # Take first volume

    # Header
    header = image.header

    # Set NAN to 0
    data[np.isnan(data)] = 0

    # Spacing for Aspect Ratio
    sX = header['pixdim'][1]
    sY = header['pixdim'][2]
    sZ = header['pixdim'][3]

    # Size per slice
    lX = data.shape[0]
    lY = data.shape[1]
    lZ = data.shape[2]

    # Validate slice number is within bounds
    if slice_num is not None:
        min_dim = min([lX, lY, lZ])  # Use explicit built-in min
        if slice_num < 0 or slice_num >= min_dim:
            raise ValueError(f"Slice number {slice_num} is out of bounds. Must be between 0 and {min_dim-1}")
        # Invert the slice numbers to match medical convention
        mX = (lX - 1 - slice_num) if slice_num < lX else int(lX / 2)
        mY = (lY - 1 - slice_num) if slice_num < lY else int(lY / 2)
        mZ = (lZ - 1 - slice_num) if slice_num < lZ else int(lZ / 2)
    else:
        mX = int(lX / 2)
        mY = int(lY / 2)
        mZ = int(lZ / 2)

    # True middle point (for crosshair)
    tmX = mX
    tmY = mY 
    tmZ = mZ

    # Orientation
    qfX = image.get_qform()[0, 0]
    sfX = image.get_sform()[0, 0]

    if qfX < 0 and (sfX == 0 or sfX < 0):
        oL = 'R'
        oR = 'L'
    elif qfX > 0 and (sfX == 0 or sfX > 0):
        oL = 'L'
        oR = 'R'
    else:
        oL = ''
        oR = ''

    if sfX < 0 and (qfX == 0 or qfX < 0):
        oL = 'R'
        oR = 'L'
    elif sfX > 0 and (qfX == 0 or qfX > 0):
        oL = 'L'
        oR = 'R'
    else:
        oL = ''
        oR = ''

    # This gives different results
    # oL = nb.aff2axcodes(image.affine)[0]


    # Plot main window
    fig = plt.figure(
        facecolor='black',
        figsize=(5, 4),
        dpi=dpi
    )

    # Black background
    plt.style.use('dark_background')

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
    min_range = np.round(np.amin(data), decimals=2)
    max_range = np.round(np.amax(data), decimals=2)
    range = ("Range: " + str(min_range) + " - " + str(max_range))

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

    if return_fig:
        return fig
    else:
        _plot_sixel(fig)


def _plot_img(iFile, return_fig=False, dpi=150):
    image = plt.imread(iFile)
    fig, ax = plt.subplots(dpi=dpi)
    ax.imshow(image)
    ax.axis('off')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    if return_fig:
        return fig
    else:
        _plot_sixel(fig)


def _is_nifti_file(filename):
    return filename.lower().endswith((".nii.gz", ".nii"))


def plot(iFile, return_fig=False, dpi=150, slice_num=None):
    if _is_nifti_file(iFile):
        return _plot_nifti_preview(iFile, return_fig=return_fig, dpi=dpi, slice_num=slice_num)
    else:
        return _plot_img(iFile, return_fig=return_fig, dpi=dpi)
