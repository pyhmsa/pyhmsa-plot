#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from pyhmsa.spec.datum.imageraster import ImageRaster2D
from pyhmsa.spec.condition.acquisition import \
    AcquisitionRasterXY, POSITION_LOCATION_CENTER, POSITION_LOCATION_START
from pyhmsa.spec.condition.specimenposition import SpecimenPosition

# Local modules.
from pyhmsa_plot.spec.datum.imageraster import ImageRaster2DPlot

# Globals and constants variables.

class TestImageRaster2DPlot(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.datum = ImageRaster2D(11, 7)
        self.datum[0, 0] = 5.0
        self.datum[2, 3] = 7

        acq = AcquisitionRasterXY(11, 7, (0.5, 'm'), (0.5, 'm'))
        acq.positions[POSITION_LOCATION_CENTER] = SpecimenPosition(0.0, 0.0, 0.0)
        acq.positions[POSITION_LOCATION_START] = SpecimenPosition((-2.5, 'm'), (1.5, 'm'), 0.0)
        self.datum.conditions.add('Acq0', acq)

        self.plot = ImageRaster2DPlot()
        self.plot.cmap = 'jet'
        self.plot.add_scalebar(location='lower center')
        self.plot.add_colorbar(width_fraction=0.02)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testplot(self):
        fig = self.plot.plot(self.datum)

        w = fig.get_figwidth()
        h = fig.get_figheight()
        self.assertAlmostEqual(w / h, 11 / 7)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
