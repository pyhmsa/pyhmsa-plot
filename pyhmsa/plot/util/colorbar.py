"""
Add color bar to matplotlib's image 
"""

# Standard library modules.
import sys
import bisect
from operator import itemgetter
import imp

# Third party modules.
from matplotlib.rcsetup import \
    (defaultParams, ValidateInStrings, validate_int, validate_float,
     validate_legend_loc, validate_bool, validate_color)
from matplotlib.artist import Artist
from matplotlib.cbook import is_string_like
from matplotlib.offsetbox import \
    AnchoredOffsetbox, AuxTransformBox, VPacker, HPacker
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.text import Text
from matplotlib.font_manager import FontProperties

import numpy as np

# Local modules.
from pyhmsa.type.unit import _PREFIXES_VALUES

# Globals and constants variables.

# Setup of extra parameters in the matplotlic rc
validate_orientation = ValidateInStrings('orientation',
                                         ['horizontal', 'vertical'])

defaultParams.update(
    {'colorbar.orientation': ['vertical', validate_orientation],
     'colorbar.nbins': [50, validate_int],
     'colorbar.length_fraction': [0.2, validate_float],
     'colorbar.width_fraction': [0.02, validate_float],
     'colorbar.location': ['upper right', validate_legend_loc],
     'colorbar.pad': [0.2, validate_float],
     'colorbar.border_pad': [0.1, validate_float],
     'colorbar.sep': [5, validate_float],
     'colorbar.frameon': [True, validate_bool],
     'colorbar.color': ['k', validate_color],
     'colorbar.box_color': ['w', validate_color],
     'colorbar.box_alpha': [1.0, validate_float],
     })

# Reload matplotlib to reset the default parameters
imp.reload(sys.modules['matplotlib'])

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

    def __init__(self, mappable, label=None, orientation=None, nbins=None,
                 length_fraction=None, width_fraction=None,
                 location=None, pad=None, border_pad=None, sep=None,
                 frameon=None, color=None, box_color=None, box_alpha=None,
                 font_properties=None):
        """
        Creates a new color bar.
        
        :arg mappable: scalar mappable object
        :arg label: label on top of the color bar
        :arg orientation: orientation, ``vertical`` or ``horizontal``
            (default: rcParams['colorbar.orientation'] or ``vertical``)
        :arg nbins: number of color division in the color bar
            (default: rcParams['colorbar.nbins'] or 50)
        :arg length_fraction: length of the color bar as a fraction of the 
            axes's width (horizontal) or height (vertical) depending on the 
            orientation (default: rcParams['colorbar.length_fraction'] or ``0.2``)
        :arg width_fraction: width of the color bar as a fraction of the 
            axes's height (horizontal) or width (vertical) depending on the
            orientation (default: rcParams['colorbar.width_fraction'] or ``0.02``
        :arg location: a location code (same as legend)
            (default: rcParams['colorbar.location'] or ``upper right``)
        :arg pad: fraction of the font size
            (default: rcParams['colorbar.pad'] or ``0.2``)
        :arg border_pad: fraction of the font size
            (default: rcParams['colorbar.border_pad'] or ``0.1``)
        :arg sep: separation between color bar and label in points
            (default: rcParams['colorbar.sep'] or ``5``)
        :arg frameon: if True, will draw a box around the color bar
            (default: rcParams['colorbar.frameon'] or ``True``)
        :arg color: color for the tick text and label
            (default: rcParams['colorbar.color'] or ``k``)
        :arg box_color: color of the box (if *frameon*)
            (default: rcParams['colorbar.box_color'] or ``w``)
        :arg box_alpha: transparency of box
            (default: rcParams['colorbar.box_alpha'] or ``1.0``)
        :arg font_properties: a matplotlib.font_manager.FontProperties instance, 
            optional sets the font properties for the label text
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
        self.font_properties = FontProperties(font_properties)

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

        # Get parameters
        from matplotlib import rcParams # late import

        cmap = self.mappable.get_cmap()
        array = self.mappable.get_array()
        label = self.label
        orientation = self.orientation or \
            rcParams.get('colorbar.orientation', 'vertical')
        nbins = self.nbins or rcParams.get('colorbar.nbins', 50)
        length_fraction = self.length_fraction or \
            rcParams.get('colorbar.length_fraction', 0.2)
        width_fraction = self.width_fraction or \
            rcParams.get('colorbar.width_fraction', 0.01)
        location = self.location or \
            self._LOCATIONS[rcParams.get('colorbar.location', 'upper right')]
        pad = self.pad or rcParams.get('colorbar.pad', 0.2)
        border_pad = self.border_pad or \
            rcParams.get('colorbar.border_pad', 0.1)
        sep = self.sep or rcParams.get('colorbar.sep', 5)
        frameon = self.frameon or rcParams.get('colorbar.frameon', True)
        color = self.color or rcParams.get('colorbar.color', 'k')
        box_color = self.box_color or rcParams.get('colorbar.box_color', 'w')
        box_alpha = self.box_alpha or rcParams.get('colorbar.box_alpha', 1.0)
        font_properties = self.font_properties

        ax = self.get_axes()
        children = []

        # Create colorbar
        colorbarbox = AuxTransformBox(ax.transData)

        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        if orientation == 'horizontal':
            length = abs(xlim[1] - xlim[0]) * length_fraction
            width = abs(ylim[1] - ylim[0]) * width_fraction
        else:
            length = abs(ylim[1] - ylim[0]) * length_fraction
            width = abs(xlim[1] - xlim[0]) * width_fraction
        step_length = length / nbins

        patches = []
        for x in np.arange(0, length, step_length):
            if orientation == 'horizontal':
                patch = Rectangle((x, 0), step_length, width)
            else:
                patch = Rectangle((0, x), width, step_length)
            patches.append(patch)

        _, values = np.histogram(array, nbins)

        col = PatchCollection(patches, cmap=cmap,
                              edgecolors='none')
        col.set_array(values)
        colorbarbox.add_artist(col)

        if orientation == 'horizontal':
            patch = Rectangle((0, 0), length, width, fill=False, ec=color)
        else:
            patch = Rectangle((0, 0), width, length, fill=False, ec=color)
        colorbarbox.add_artist(patch)

        children.append(colorbarbox)

        # Create ticks
        tickbox = AuxTransformBox(ax.transData)

        if orientation == 'horizontal':
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
                     color=color,
                     fontproperties=font_properties,
                     horizontalalignment=ha,
                     verticalalignment=va)
        tickbox.add_artist(tick0)

        tick1 = Text(x1, y1, values[-1],
                     color=color,
                     fontproperties=font_properties,
                     horizontalalignment=ha,
                     verticalalignment=va)
        tickbox.add_artist(tick1)

        children.append(tickbox)

        # Create label
        if label:
            labelbox = AuxTransformBox(ax.transData)

            va = 'baseline' if orientation == 'horizontal' else 'center'
            text = Text(0, 0, label,
                        fontproperties=font_properties,
                        verticalalignment=va,
                        rotation=orientation)
            labelbox.add_artist(text)

            children.insert(0, labelbox)

        # Create final offset box
        Packer = VPacker if orientation == 'horizontal' else HPacker
        child = Packer(children=children, align="center", pad=0, sep=sep)

        box = AnchoredOffsetbox(loc=location,
                                pad=pad,
                                borderpad=border_pad,
                                child=child,
                                frameon=frameon)

        box.set_axes(ax)
        box.set_figure(self.get_figure())
        box.patch.set_color(box_color)
        box.patch.set_alpha(box_alpha)
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
        if orientation is not None and \
                orientation not in ['vertical', 'horizontal']:
            raise ValueError('Unknown orientation: %s' % orientation)
        self._orientation = orientation

    @property
    def nbins(self):
        return self._nbins

    @nbins.setter
    def nbins(self, nbins):
        if nbins is not None:
            nbins = int(nbins)
            if nbins <= 0:
                raise ValueError('Number of bins must be greater than 0')
        self._nbins = nbins

    @property
    def length_fraction(self):
        return self._length_fraction

    @length_fraction.setter
    def length_fraction(self, fraction):
        if fraction is not None:
            fraction = float(fraction)
            if fraction < 0.0 or fraction > 1.0:
                raise ValueError('Length fraction must be between [0.0, 1.0]')
        self._length_fraction = fraction

    @property
    def width_fraction(self):
        return self._width_fraction

    @width_fraction.setter
    def width_fraction(self, fraction):
        if fraction is not None:
            fraction = float(fraction)
            if fraction < 0.0 or fraction > 1.0:
                raise ValueError('Width fraction must be between [0.0, 1.0]')
        self._width_fraction = fraction

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
        self._pad = pad

    @property
    def border_pad(self):
        return self._border_pad

    @border_pad.setter
    def border_pad(self, pad):
        self._border_pad = pad

    @property
    def sep(self):
        return self._sep

    @sep.setter
    def sep(self, sep):
        self._sep = sep

    @property
    def frameon(self):
        return self._frameon

    @frameon.setter
    def frameon(self, on):
        self._frameon = on

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
        if alpha is not None:
            alpha = float(alpha)
            if alpha < 0.0 or alpha > 1.0:
                raise ValueError('Alpha must be between [0.0, 1.0]')
        self._box_alpha = alpha

    @property
    def font_properties(self):
        return self._font_properties

    @font_properties.setter
    def font_properties(self, props):
        self._font_properties = props

