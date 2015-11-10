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

    def __init__(self, datum=None):
        _DatumPlot.__init__(self, datum=datum)

        # Properties
        self._cmap = None

        # Create color bar
        self._colorbar = ColorBar()
        self.add_figure_artist(self._colorbar)

        # Create scale bar
        self._scalebar = ScaleBar(0)
        self.add_figure_artist(self._scalebar)

    def _create_figure(self, datum):
        acqs = datum.conditions.findvalues(AcquisitionRasterXY)
        acq = next(iter(acqs)) if acqs else None

        # Create figure
        fig = Figure()

        # Re-adjust height
        width, height = datum.shape
        fig.set_figheight(fig.get_figwidth() * height / width)

        # Create axes
        ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
        fig.subplots_adjust(0, 0, 1.0, 1.0)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
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

            if acq and acq.step_size_x is not None and acq.step_size_y is not None:
                dx_m = convert_unit('m', acq.step_size_x)
                dy_m = convert_unit('m', acq.step_size_y)
                extent = [0.0, dx_m * width, 0.0, dy_m * height]

        aximage = ax.imshow(datum, cmap=self._cmap, extent=extent,
                            interpolation='none')

        if not acq:
            self._scalebar.set_visible(False)
            self._scalebar.set_dx_m(0)
        else:
            self._scalebar.set_dx_m(1)

        self._colorbar.set_mappable(aximage)

        return fig, [ax]

    @property
    def cmap(self):
        mappable = self._colorbar.get_mappable()
        if mappable:
            return mappable.get_cmap()
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        mappable = self._colorbar.get_mappable()
        if mappable:
            mappable.set_cmap(cmap)
        else:
            self._cmap = cmap

    @property
    def scalebar(self):
        return self._scalebar

    @property
    def colorbar(self):
        return self._colorbar

