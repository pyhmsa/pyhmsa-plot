""""""

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
from pyhmsa_plot.spec.datum.datum import _DatumPlot

# Globals and constants variables.

class AnalysisList0DPlot(_DatumPlot):

    def _plot(self, datum, ax):
        xs = np.arange(len(datum))
        ys = datum[:, 0]
        xlabel = datum.get_xlabel()
        ylabel = datum.get_ylabel()

        # Draw
        ax.plot(xs, ys, zorder=1)

        # Labels
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
