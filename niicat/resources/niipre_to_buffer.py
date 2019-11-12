
import sys
import matplotlib.pyplot as plt
from niicat.niipre import plot_preview

iFile = sys.argv[1]
fig = plot_preview(iFile, return_fig=True)
# fig = plt.gcf()
plt.savefig(sys.stdout.buffer, dpi=120)