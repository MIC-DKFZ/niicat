#!/usr/bin/env python

import argparse
import subprocess
from importlib.metadata import version
from importlib.resources import files as resource_files


def is_executable(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None


def is_nifti_file(filename):
    return filename.lower().endswith((".nii.gz", ".nii"))


def run_nifti_preview(display_command, filename, dpi, slice_num):
    from niicat.nifti_preview import save_nifti_preview

    with subprocess.Popen(display_command, stdin=subprocess.PIPE) as display:
        save_nifti_preview(filename, display.stdin, dpi=dpi, slice_num=slice_num)
        display.stdin.close()
        return display.wait()


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
    if args.ls:
        from niicat.plotter import plot
        plot(args.nifti_file, dpi=args.dpi, slice_num=args.slice)
        return

    if args.lb:
        display_command = ["img2sixel"]
        if not is_executable(display_command[0]):
            print("ERROR: the command 'img2sixel' is not available in your PATH. " +
                  "Install libsixel-bin to make it available.")
            return
    else:
        display_command = [str(niicat_files / 'imgcat.sh')]

    # iTerm2 and img2sixel can decode ordinary image files themselves. Sending
    # the original compressed file avoids a costly Matplotlib decode, redraw,
    # and re-encode cycle (and its large memory allocation).
    if not is_nifti_file(args.nifti_file):
        if args.lb:
            image_command = display_command
        else:
            # Match Matplotlib's previous default 6.4 x 4.8 inch canvas while
            # leaving the compressed source image untouched.
            image_command = display_command + [
                "--width", f"{round(6.4 * args.dpi)}px",
                "--height", f"{round(4.8 * args.dpi)}px",
            ]
        subprocess.run(image_command + [args.nifti_file])
        return

    run_nifti_preview(
        display_command,
        args.nifti_file,
        args.dpi,
        args.slice,
    )


if __name__ == '__main__':
    main() 