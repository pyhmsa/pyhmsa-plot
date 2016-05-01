""""""

# Standard library modules.

# Third party modules.
from matplotlib_colorbar.colorbar import Colorbar
from matplotlib_scalebar.scalebar import ScaleBar

import numpy as np

from pyhmsa.spec.condition.acquisition import AcquisitionRasterXY
from pyhmsa.type.numerical import convert_unit

# Local modules.
from pyhmsa_plot.spec.datum.datum import _DatumPlot
from pyhmsa_plot.util.modest_image import imshow

# Globals and constants variables.

class ImageRaster2DPlot(_DatumPlot):

    def __init__(self):
        super().__init__()

        self.cmap = None
        self.vmin = None
        self.vmax = None
        self.unit = 'm'
        self._colorbar_kwargs = None
        self._scalebar_kwargs = None

    def _create_axes(self, fig, datum):
        return fig.add_axes([0.0, 0.0, 1.0, 1.0])

    def _create_figure(self, datum):
        fig, ax = _DatumPlot._create_figure(self, datum)

        width, height = datum.shape
        fig.set_figheight(fig.get_figwidth() * height / width)

        return fig, ax

    def _plot(self, datum, ax):
        acqs = datum.conditions.findvalues(AcquisitionRasterXY)
        acq = next(iter(acqs)) if acqs else None

        # Setup axes
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        # Plot datum
        unit = self.unit
        try:
            p0 = datum.get_position(0, 0)
            p1 = datum.get_position(-1, -1)

            p0x = float(convert_unit(unit, p0.x))
            p0y = float(convert_unit(unit, p0.y))
            p1x = float(convert_unit(unit, p1.x))
            p1y = float(convert_unit(unit, p1.y))

            datum = np.flipud(datum.T)
            if p0x > p1x:
                datum = np.fliplr(datum)
                p0x, p1x = p1x, p0x
            if p0y > p1y:
                datum = np.flipud(datum)
                p0y, p1y = p1y, p0y

            extent = [p0x, p1x, p0y, p1y]

        except:
            extent = None

        aximage = imshow(ax, datum, cmap=self.cmap, extent=extent,
                         interpolation='none',
                         vmin=self.vmin, vmax=self.vmax)

        if acq and self._scalebar_kwargs is not None:
            scalebar = ScaleBar(1, **self._scalebar_kwargs)
            ax.add_artist(scalebar)

        if self._colorbar_kwargs is not None:
            colorbar = Colorbar(aximage, **self._colorbar_kwargs)
            ax.add_artist(colorbar)

    def add_colorbar(self, **kwargs):
        if self._colorbar_kwargs is not None:
            raise ValueError('Colorbar already defined')
        self._colorbar_kwargs = kwargs

    def add_scalebar(self, **kwargs):
        if self._scalebar_kwargs is not None:
            raise ValueError('Scalebar already defined')
        self._scalebar_kwargs = kwargs
