""""""

# Standard library modules.

# Third party modules.
from matplotlib_colorbar.colorbar import Colorbar
from matplotlib_scalebar.scalebar import ScaleBar

import numpy as np

import scipy.ndimage as ndimage

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
        self._median_filter_kwargs = None

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

        # Plot
        datum, extent = self._calculate_extent(datum)
        datum = self._apply_median(datum)

        aximage = imshow(ax, datum, cmap=self.cmap, extent=extent,
                         interpolation='none',
                         vmin=self.vmin, vmax=self.vmax)

        self._apply_scalebar(datum, ax, extent)
        self._apply_colorbar(datum, ax, aximage)

    def _calculate_extent(self, datum):
        unit = self.unit
        try:
            p0 = datum.get_position(0, 0)
            p1 = datum.get_position(-1, -1)

            p0x = float(convert_unit(unit, p0.x))
            p0y = float(convert_unit(unit, p0.y))
            p1x = float(convert_unit(unit, p1.x))
            p1y = float(convert_unit(unit, p1.y))

            datum = np.flipud(datum.T)
            datum = np.rot90(datum, 2)
            if p0x > p1x:
                datum = np.fliplr(datum)
                p0x, p1x = p1x, p0x
            if p0y > p1y:
                datum = np.flipud(datum)
                p0y, p1y = p1y, p0y

            return datum, [p0x, p1x, p0y, p1y]

        except:
            pass

        return datum, None

    def add_colorbar(self, **kwargs):
        if self._colorbar_kwargs is not None:
            raise ValueError('Colorbar already defined')
        self._colorbar_kwargs = kwargs

    def remove_colorbar(self):
        self._colorbar_kwargs = None

    def has_colorbar(self):
        return self._colorbar_kwargs is not None

    def get_colorbar_kwargs(self):
        if not self.has_colorbar():
            return {}
        return self._colorbar_kwargs.copy()

    def _apply_colorbar(self, datum, ax, aximage):
        if not self.has_colorbar():
            return
        colorbar = Colorbar(aximage, **self._colorbar_kwargs)
        ax.add_artist(colorbar)

    def add_scalebar(self, **kwargs):
        if self._scalebar_kwargs is not None:
            raise ValueError('Scalebar already defined')
        self._scalebar_kwargs = kwargs

    def remove_scalebar(self):
        self._scalebar_kwargs = None

    def has_scalebar(self):
        return self._scalebar_kwargs is not None

    def get_scalebar_kwargs(self):
        if not self.has_scalebar():
            return {}
        return self._scalebar_kwargs.copy()

    def _apply_scalebar(self, datum, ax, extent):
        if not self.has_scalebar():
            return
        if extent is None:
            return
        scalebar = ScaleBar(1, **self._scalebar_kwargs)
        ax.add_artist(scalebar)

    def add_median_filter(self, size=3):
        if self.has_median_filter():
            raise ValueError('Median filter already defined')
        self._median_filter_kwargs = {'size': size}

    def remove_median_filter(self):
        self._median_filter_kwargs = None

    def has_median_filter(self):
        return self._median_filter_kwargs is not None

    def _apply_median(self, datum):
        if not self.has_median_filter():
            return datum
        return ndimage.median_filter(datum, **self._median_filter_kwargs)
