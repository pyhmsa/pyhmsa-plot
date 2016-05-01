""""""

# Standard library modules.

# Third party modules.
import matplotlib

import numpy as np

from matplotlib_colorbar.colorbar import Colorbar

# Local modules.
from pyhmsa_plot.spec.datum.datum import _DatumPlot
from pyhmsa_plot.util.modest_image import imshow

# Globals and constants variables.

class Analysis1DPlot(_DatumPlot):

    def __init__(self):
        super().__init__()

        self._selected_xs = []
        self._selected_ranges = []

    def add_selected_x(self, x):
        self._selected_xs.append(x)

    def add_selected_range(self, xmin, xmax):
        self._selected_ranges.append((xmin, xmax))

    def _plot(self, datum, ax):
        # Extract data and labels
        xy = datum.get_xy()
        xlabel = datum.get_xlabel()
        ylabel = datum.get_ylabel()

        # Draw
        colors = matplotlib.rcParams['axes.prop_cycle'].by_key()['color']

        ax.plot(xy[:, 0], xy[:, 1], lw=2, color=colors[0], zorder=1)

        for x in self._selected_xs:
            ax.axvline(x, lw=3, color=colors[1], zorder=3)

        for xmin, xmax in self._selected_ranges:
            ax.axvspan(xmin, xmax, alpha=0.5, facecolor=colors[2], zorder=3)

        # Labels
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

class Analysis2DPlot(_DatumPlot):

    def __init__(self):
        super().__init__()

        self.cmap = None
        self.vmin = None
        self.vmax = None
        self._colorbar_kwargs = None

    def _create_axes(self, fig, datum):
        return fig.add_axes([0.0, 0.0, 1.0, 1.0])

    def _create_figure(self, datum):
        fig, ax = _DatumPlot._create_figure(self, datum)

        width, height = datum.shape
        fig.set_figheight(fig.get_figwidth() * height / width)

        return fig, ax

    def _plot(self, datum, ax):
        # Setup axes
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        # Plot datum
        datum = np.flipud(datum.T)
        extent = None

        aximage = imshow(ax, datum, cmap=self.cmap, extent=extent,
                         interpolation='none',
                         vmin=self.vmin, vmax=self.vmax)

        if self._colorbar_kwargs is not None:
            colorbar = Colorbar(aximage, **self._colorbar_kwargs)
            ax.add_artist(colorbar)

    def add_colorbar(self, **kwargs):
        if self._colorbar_kwargs is not None:
            raise ValueError('Colorbar already defined')
        self._colorbar_kwargs = kwargs

