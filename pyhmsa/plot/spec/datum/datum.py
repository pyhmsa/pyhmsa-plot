""""""

# Standard library modules.
import os
import abc

# Third party modules.

# Local modules.
import matplotlib.backend_bases

# Globals and constants variables.

class _DatumPlot(object, metaclass=abc.ABCMeta):

    def __init__(self, datum=None):
        self._figure = None
        self._figure_artists = set()
        self.datum = datum

    @abc.abstractmethod
    def _create_figure(self, datum):
        """
        Creates a figure plotting the specified datum.
        
        :return: :class:`matplotlib.figure.Figure` 
            and a list of the created :class:`matplotlib._axes.Axes`
        """
        raise NotImplementedError

    def _reset_figure(self):
        self._figure = None

    def has_figure(self):
        return self._figure is not None

    def add_figure_artist(self, artist):
        self._figure_artists.add(artist)

    def remove_figure_artist(self, artist):
        self._figure_artists.discard(artist)

    def clear_figure_artists(self):
        self._figure_artists.clear()

    def get_figure(self):
        if self._datum is None:
            raise RuntimeError('No datum is specified')

        if not self.has_figure():
            self._figure, axes = self._create_figure(self._datum)
            for ax in axes:
                for artist in self._figure_artists:
                    ax.add_artist(artist)

        return self._figure

    def save(self, filepath, canvas_class=None, *args, **kwargs):
        if canvas_class is None:
            ext = os.path.splitext(filepath)[1][1:]
            canvas_class = matplotlib.backend_bases.get_registered_canvas_class(ext)

        figure = self.get_figure()
        canvas_class(figure)
        figure.savefig(filepath, *args, **kwargs)

    def get_datum(self):
        return self._datum

    def set_datum(self, datum):
        self._reset_figure()
        self._datum = datum

    datum = property(get_datum, set_datum)
