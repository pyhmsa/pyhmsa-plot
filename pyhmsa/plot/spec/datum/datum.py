""""""

# Standard library modules.
import os

# Third party modules.

# Local modules.
import matplotlib.backend_bases

# Globals and constants variables.

class _DatumPlot(object):

    def __init__(self, datum, *args, **kwargs):
        self._datum = datum
        self._figure = self._create_figure(datum, *args, **kwargs)

    def _create_figure(self, datum, *args, **kwargs):
        raise NotImplementedError

    def save(self, filepath, canvas_class=None, *args, **kwargs):
        if canvas_class is None:
            ext = os.path.splitext(filepath)[1][1:]
            canvas_class = matplotlib.backend_bases.get_registered_canvas_class(ext)

        canvas_class(self._figure)
        self._figure.savefig(filepath, *args, **kwargs)

    @property
    def datum(self):
        return self._datum

