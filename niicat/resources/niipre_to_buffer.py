
import sys
import matplotlib.pyplot as plt
from niicat.plotter import plot

iFile = sys.argv[1]
dpi = int(sys.argv[2])
fig = plot(iFile, return_fig=True)
plt.savefig(sys.stdout.buffer, dpi=dpi)