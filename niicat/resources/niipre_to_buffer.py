import sys
from niicat.nifti_preview import save_nifti_preview

iFile = sys.argv[1]
dpi = int(sys.argv[2])
slice_num = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
save_nifti_preview(iFile, sys.stdout.buffer, dpi=dpi, slice_num=slice_num)