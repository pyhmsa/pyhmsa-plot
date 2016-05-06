""""""

# Standard library modules.
import os
import abc

# Third party modules.

# Local modules.
import matplotlib.backend_bases
from matplotlib.figure import Figure

# Globals and constants variables.

class _DatumPlot(object, metaclass=abc.ABCMeta):

    def _create_axes(self, fig, datum):
        return fig.add_subplot("111")

    def _create_figure(self, datum):
        fig = Figure()
        ax = self._create_axes(fig, datum)
        return fig, ax

    @abc.abstractmethod
    def _plot(self, datum, ax):
        """
        Performs the actual plotting of *datum* in *ax*.
        """
        raise NotImplementedError

    def plot(self, datum, ax=None):
        """
        Plots the datum in a matplotlib :class:`Axes <matplotlib.axes.Axes>`.
        If no *ax* is specified a figure and axes is created.
        
        :arg datum: datum object 
        :type datum: :class:`pyhmsa.spec.datum.datum._Datum`
        
        :arg ax: matplotlib's Axes (optional)
        :type ax: class:`Axes <matplotlib.axes.Axes>`
        
        :return: matplotlib's Figure
        :rtype: :class:`matplotlib.figure.Figure`
        """
        if ax is None:
            fig, ax = self._create_figure(datum)
        else:
            fig = ax.get_figure()

        ax.clear()
        self._plot(datum, ax)

        return fig

    def save(self, filepath, datum, ax=None, canvas_class=None, *args, **kwargs):
        """
        Plots and saves the *datum* to the specified *filepath*.
        """
        fig = self.plot(datum, ax)

        if canvas_class is None:
            ext = os.path.splitext(filepath)[1][1:]
            canvas_class = matplotlib.backend_bases.get_registered_canvas_class(ext)

        canvas_class(fig)
        fig.savefig(filepath, *args, **kwargs)

        if ax is None:
            del fig
            del canvas_class

