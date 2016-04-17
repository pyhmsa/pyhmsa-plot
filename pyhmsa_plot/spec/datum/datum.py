""""""

# Standard library modules.
import os
import abc
from operator import attrgetter

# Third party modules.

# Local modules.
import matplotlib.backend_bases

# Globals and constants variables.

class _DatumPlot(object, metaclass=abc.ABCMeta):

    def __init__(self):
        self._figure = self._create_figure()
        self._cached_artists = set()
        self._datum = None

    @abc.abstractmethod
    def _create_figure(self):
        """
        Creates a figure containing no datum, but ready to be drawn.
        
        :return: :class:`matplotlib.figure.Figure` 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _draw_datum(self, figure, datum):
        """
        Draws datum in figure.
        """
        raise NotImplementedError

    def _apply_to_axes(self, methodname, *args, **kwargs):
        outs = []
        excs = []

        for ax in self._figure.axes:
            method = attrgetter(methodname)(ax)
            try:
                out = method(*args, **kwargs)
                outs.append(out)
            except Exception as ex:
                excs.append(ex)

        if excs:
            raise Exception(', '.join(map(str, excs)))

        return outs

    def add_artist(self, artist):
        self._apply_to_axes('add_artist', artist)
        self._cached_artists.add(artist)

    def remove_artist(self, artist):
        try:
            self._apply_to_axes('artists.remove', artist)
        except:
            pass
        self._cached_artists.discard(artist)

    def draw(self):
        for artist in self._cached_artists:
            try:
                artist.remove()
            except NotImplementedError:
                pass
        self._figure.clear()

        datum = self._datum
        if datum is None:
            return

        self._draw_datum(self._figure, datum)

        for artist in self._cached_artists:
            self._apply_to_axes('add_artist', artist)

    def clear(self):
        self._cached_artists.clear()
        self.draw()

    def save(self, filepath, canvas_class=None, *args, **kwargs):
        if canvas_class is None:
            ext = os.path.splitext(filepath)[1][1:]
            canvas_class = matplotlib.backend_bases.get_registered_canvas_class(ext)

        figure = self.get_figure()
        canvas_class(figure)
        figure.savefig(filepath, *args, **kwargs)

    def get_figure(self):
        return self._figure

    figure = property(get_figure)

    def get_datum(self):
        return self._datum

    def set_datum(self, datum):
        if datum is self._datum:
            return
        self._datum = datum
        self.draw()

    datum = property(get_datum, set_datum)
