"""
Add scale bar to matplotlib's image 
"""

# Standard library modules.
import bisect
from operator import itemgetter

# Third party modules.
from matplotlib.artist import Artist
from matplotlib.cbook import is_string_like

from matplotlib.offsetbox import \
    AnchoredOffsetbox, AuxTransformBox, VPacker, HPacker
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.text import Text

import numpy as np

# Local modules.
from pyhmsa.type.unit import _PREFIXES_VALUES

# Globals and constants variables.

class ColorBar(Artist):

    zorder = 5

    _LOCATIONS = {'upper right':  1,
                  'upper left':   2,
                  'lower left':   3,
                  'lower right':  4,
                  'right':        5,
                  'center left':  6,
                  'center right': 7,
                  'lower center': 8,
                  'upper center': 9,
                  'center':       10,
              }

    def __init__(self, mappable, label=None, orientation='vertical', nbins=50,
                 length_fraction=0.2, width_fraction=0.01,
                 location=1, pad=0.2, border_pad=0.1, sep=5, frameon=True,
                 color='k', box_color='w', box_alpha=1.0,
                 label_top=False, font_properties=None,
                 **kwargs):
        """
        Creates a new scale bar.
        
        :arg dx_m: dimension of one pixel in meters (m)
        :arg length_fraction: length of the scale bar as a fraction of the 
            axes's width
        :arg height_fraction: height of the scale bar as a fraction of the 
            axes's height
        :arg location: a location code (same as legend)
        :arg pad: fraction of the legend font size
        :arg border_pad : fraction of the legend font size
        :arg sep : separation between scale bar and label in points
        :arg frameon : if True, will draw a box around the horizontal bar and label
        :arg color : color for the size bar and label
        :arg box_color: color of the box (if *frameon*)
        :arg box_alpha: transparency of box
        :arg label_top : if True, the label will be over the rectangle
        :arg font_properties: a matplotlib.font_manager.FontProperties instance, optional
            sets the font properties for the label text
        """
        Artist.__init__(self)

        self.mappable = mappable
        self.label = label
        self.orientation = orientation
        self.nbins = nbins
        self.length_fraction = length_fraction
        self.width_fraction = width_fraction
        self.location = location
        self.pad = pad
        self.border_pad = border_pad
        self.sep = sep
        self.frameon = frameon
        self.color = color
        self.box_color = box_color
        self.box_alpha = box_alpha
        self.label_top = label_top
        self.font_properties = font_properties
        self._kwargs = kwargs

    def _calculate_length(self, length_px):
        length_m = length_px * self._dx_m

        prefixes_values = _PREFIXES_VALUES.copy()
        prefixes_values[''] = 1.0
        prefixes_values.pop('u')
        prefixes_values = sorted(prefixes_values.items(), key=itemgetter(1))
        values = [prefix_value[1] for prefix_value in prefixes_values]
        index = bisect.bisect_left(values, length_m)
        unit, factor = prefixes_values[index - 1]

        length_unit = length_m / factor
        index = bisect.bisect_left(self._PREFERRED_VALUES, length_unit)
        length_unit = self._PREFERRED_VALUES[index - 1]

        length_px = length_unit * factor / self._dx_m
        label = '%i %sm' % (length_unit, unit)

        return length_px, label

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return

        ax = self.get_axes()
        children = []

        # Create colorbar
        colorbarbox = AuxTransformBox(ax.transData)

        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        if self.orientation == 'horizontal':
            length = abs(xlim[1] - xlim[0]) * self.length_fraction
            width = abs(ylim[1] - ylim[0]) * self.width_fraction
        else:
            length = abs(ylim[1] - ylim[0]) * self.length_fraction
            width = abs(xlim[1] - xlim[0]) * self.width_fraction
        step_length = length / self.nbins

        patches = []
        for x in np.arange(0, length, step_length):
            if self.orientation == 'horizontal':
                patch = Rectangle((x, 0), step_length, width)
            else:
                patch = Rectangle((0, x), width, step_length)
            patches.append(patch)

        _, values = np.histogram(self.mappable.get_array(), self.nbins)

        col = PatchCollection(patches, cmap=self.mappable.get_cmap(),
                              edgecolors='none')
        col.set_array(values)
        colorbarbox.add_artist(col)

        if self.orientation == 'horizontal':
            patch = Rectangle((0, 0), length, width, fill=False, ec=self.color)
        else:
            patch = Rectangle((0, 0), width, length, fill=False, ec=self.color)
        colorbarbox.add_artist(patch)

        children.append(colorbarbox)

        # Create ticks
        tickbox = AuxTransformBox(ax.transData)

        if self.orientation == 'horizontal':
            x0 = 0; x1 = length
            y0 = y1 = 0
            ha = 'center'
            va = 'top'
        else:
            x0 = x1 = width
            y0 = 0; y1 = length
            ha = 'left'
            va = 'center'

        tick0 = Text(x0, y0, values[0],
                     color=self.color, fontproperties=self.font_properties,
                     horizontalalignment=ha, verticalalignment=va)
        tickbox.add_artist(tick0)

        tick1 = Text(x1, y1, values[-1],
                     color=self.color, fontproperties=self.font_properties,
                     horizontalalignment=ha, verticalalignment=va)
        tickbox.add_artist(tick1)

        children.append(tickbox)

        # Create label
        if self.label:
            labelbox = AuxTransformBox(ax.transData)

            va = 'baseline' if self.orientation == 'horizontal' else 'center'
            text = Text(0, 0, self.label,
                        verticalalignment=va, rotation=self.orientation)
            labelbox.add_artist(text)

            children.insert(0, labelbox)

        # Create final offset box
        Packer = VPacker if self.orientation == 'horizontal' else HPacker
        child = Packer(children=children, align="center", pad=0, sep=self.sep)

        box = AnchoredOffsetbox(loc=self.location,
                                pad=self.pad,
                                borderpad=self.border_pad,
                                child=child,
                                frameon=self.frameon)

        box.set_axes(ax)
        box.set_figure(self.get_figure())
        box.patch.set_color(self.box_color)
        box.patch.set_alpha(self.box_alpha)
        box.draw(renderer)

    @property
    def mappable(self):
        return self._mappable

    @mappable.setter
    def mappable(self, mappable):
        self._mappable = mappable

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        if orientation not in ['vertical', 'horizontal']:
            raise ValueError('Unknown orientation: %s' % orientation)
        self._orientation = orientation

    @property
    def nbins(self):
        return self._nbins

    @nbins.setter
    def nbins(self, nbins):
        nbins = int(nbins)
        if nbins <= 0:
            raise ValueError('Number of bins must be greater than 0')
        self._nbins = nbins

    @property
    def length_fraction(self):
        return self._length_fraction

    @length_fraction.setter
    def length_fraction(self, fraction):
        assert 0.0 <= fraction <= 1.0
        self._length_fraction = float(fraction)

    @property
    def width_fraction(self):
        return self._width_fraction

    @width_fraction.setter
    def width_fraction(self, fraction):
        assert 0.0 <= fraction <= 1.0
        self._width_fraction = float(fraction)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, loc):
        if is_string_like(loc):
            if loc not in self._LOCATIONS:
                raise ValueError('Unknown location code: %s' % loc)
            loc = self._LOCATIONS[loc]
        self._location = loc

    @property
    def pad(self):
        return self._pad

    @pad.setter
    def pad(self, pad):
        self._pad = float(pad)

    @property
    def border_pad(self):
        return self._border_pad

    @border_pad.setter
    def border_pad(self, pad):
        self._border_pad = float(pad)

    @property
    def sep(self):
        return self._sep

    @sep.setter
    def sep(self, sep):
        self._sep = float(sep)

    @property
    def frameon(self):
        return self._frameon

    @frameon.setter
    def frameon(self, on):
        self._frameon = bool(on)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def box_color(self):
        return self._box_color

    @box_color.setter
    def box_color(self, color):
        self._box_color = color

    @property
    def box_alpha(self):
        return self._box_alpha

    @box_alpha.setter
    def box_alpha(self, alpha):
        assert 0.0 <= alpha <= 1.0
        self._box_alpha = alpha

    @property
    def label_top(self):
        return self._label_top

    @label_top.setter
    def label_top(self, top):
        self._label_top = bool(top)

    @property
    def font_properties(self):
        return self._font_properties

    @font_properties.setter
    def font_properties(self, props):
        self._font_properties = props

