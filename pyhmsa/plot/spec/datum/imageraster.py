""""""

# Standard library modules.

# Third party modules.
from matplotlib.figure import Figure

import numpy as np

from pyhmsa.spec.condition.acquisition import AcquisitionRasterXY
from pyhmsa.type.numerical import convert_unit

# Local modules.
from pyhmsa.plot.spec.datum.datum import _DatumPlot
from pyhmsa.plot.util.scalebar import ScaleBar
from pyhmsa.plot.util.colorbar import ColorBar

# Globals and constants variables.

class ImageRaster2DPlot(_DatumPlot):

    def _create_figure(self, datum, *args, **kwargs):
        acqs = datum.conditions.findvalues(AcquisitionRasterXY)
        acq = next(iter(acqs)) if acqs else None

        # Create figure
        fig = Figure(*args, **kwargs)

        # Re-adjust height
        width, height = datum.shape
        fig.set_figheight(fig.get_figwidth() * height / width)

        # Create axes
        self._ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
        fig.subplots_adjust(0, 0, 1.0, 1.0)
        self._ax.xaxis.set_visible(False)
        self._ax.yaxis.set_visible(False)
#        self._ax = fig.add_subplot("111")

        # Plot datum
        extent = None
        try:
            p0 = datum.get_position(0, 0)
            p1 = datum.get_position(-1, -1)

            p0x = float(convert_unit('m', p0.x))
            p0y = float(convert_unit('m', p0.y))
            p1x = float(convert_unit('m', p1.x))
            p1y = float(convert_unit('m', p1.y))

            datum = np.flipud(datum.T)
            if p0x > p1x:
                datum = np.fliplr(datum)
                p0x, p1x = p1x, p0x
            if p0y > p1y:
                datum = np.flipud(datum)
                p0y, p1y = p1y, p0y

            extent = [p0x, p1x, p0y, p1y]

        except:
            datum = np.flipud(datum.T)

            if acq.step_size_x is not None and acq.step_size_y is not None:
                dx_m = convert_unit('m', acq.step_size_x)
                dy_m = convert_unit('m', acq.step_size_y)
                extent = [0.0, dx_m * width, 0.0, dy_m * height]

        self._aximage = self._ax.imshow(datum, extent=extent,
                                        interpolation='none')

        self._scalebar = None
        if acq:
            self._scalebar = self._create_scalebar(acq)
            self._ax.add_artist(self._scalebar)

        self._colorbar = ColorBar(self._aximage)
        self._ax.add_artist(self._colorbar)

        return fig

    def _create_colorbar(self, fig, ax, aximage):
        return fig.colorbar(aximage, ax=ax, shrink=0.8)

    def _create_scalebar(self, acq):
        return ScaleBar(1) # 1 because already calibrated by extent

    def add_artist(self, artist):
        self._ax.add_artist(artist)

    @property
    def cmap(self):
        return self._aximage.get_cmap()

    @cmap.setter
    def cmap(self, cmap):
        self._aximage.set_cmap(cmap)

    @property
    def scalebar(self):
        if self._scalebar is None:
            raise RuntimeError('No scale bar')
        return self._scalebar

    @property
    def colorbar(self):
        return self._colorbar

