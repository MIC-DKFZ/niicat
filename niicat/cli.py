#!/usr/bin/env python

import os
import sys
import argparse
from niicat.plotter import plot
from importlib.metadata import files, version
from importlib.resources import files as resource_files

def is_executable(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None


def main():
    parser = argparse.ArgumentParser(description="Generate previews of nifti image and png/jpeg images " +
                                                 "on the terminal.",
                                    epilog="Written by Jakob Wasserthal")
    parser.add_argument("nifti_file")
    parser.add_argument("-ls", action="store_true",
                        help="Use libsixel-python instead of iTerm2's imgcat to plot the image.",
                        default=False)
    parser.add_argument("-lb", action="store_true",
                        help="Use libsixel-bin instead of iTerm2's imgcat to plot the image.",
                        default=False)
    parser.add_argument("-d", "--dpi", metavar="N", type=int,
                        help="resolution for plotting (default: 200).",
                        default=200)
    parser.add_argument("-s", "--slice", metavar="N", type=int,
                        help="slice number to show (default: middle slice)",
                        default=None)
    parser.add_argument('--version', action='version', version=version("niicat"))
    args = parser.parse_args()

    niicat_files = resource_files('niicat.resources')
    python_path = sys.executable if sys.executable else "python"
    if args.ls:
        plot(args.nifti_file, dpi=args.dpi, slice_num=args.slice)
    elif args.lb:
        niipre_path = str(niicat_files / 'niipre_to_buffer.py')
        imgcat_path = "img2sixel"
        if is_executable(imgcat_path):
            os.system(python_path + " " + niipre_path + " " + args.nifti_file + " " + str(args.dpi) + 
                     " " + str(args.slice if args.slice is not None else "") + " | " + imgcat_path)
        else:
            print("ERROR: the command 'img2sixel' is not available in your PATH. " +
                  "Install libsixel-bin to make it available.")
    else:
        niipre_path = str(niicat_files / 'niipre_to_buffer.py')
        imgcat_path = str(niicat_files / 'imgcat.sh')
        os.system(python_path + " " + niipre_path + " " + args.nifti_file + " " + str(args.dpi) + 
                 " " + str(args.slice if args.slice is not None else "") + " | " + imgcat_path)


if __name__ == '__main__':
    main() 
