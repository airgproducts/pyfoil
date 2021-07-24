#! /usr/bin/python2
# -*- coding: utf-8; -*-
#
# (c) 2013 booya (http://booya.at)
#
# This file is part of the OpenGlider project.
#
# OpenGlider is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# OpenGlider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenGlider.  If not, see <http://www.gnu.org/licenses/>.

import os
import tempfile
import unittest
import random

from pyfoil import Airfoil

TEMPDIR =  tempfile.gettempdir()

class TestNaca(unittest.TestCase):
    def setUp(self):
        self.airfoil = Airfoil.compute_naca(1222, numpoints=150)

    def assertEqualAirfoil(self, airfoil1, airfoil2):
        self.assertAlmostEqual(airfoil1.thickness, airfoil2.thickness)
        self.assertAlmostEqual(airfoil1.camber, airfoil2.camber)
        self.assertEqual(airfoil1.numpoints, airfoil2.numpoints)

    def test_export(self):
        path = os.path.join(TEMPDIR, "prof.dat")
        self.airfoil.export_dat(path)
        airfoil2 = Airfoil.import_from_dat(path)
        
        self.assertEqualAirfoil(self.airfoil, airfoil2)

    def test_numpoints(self):
        num = random.randint(4, 500)
        prof2 = self.airfoil.resample(num)

        self.assertEqual(num + 1 - num % 2, prof2.numpoints)


    def test_profilepoint(self):
        x = random.random() * random.randint(-1, 1)
        self.assertAlmostEqual(abs(x), self.airfoil.profilepoint(x)[0])

    def test_multiplication(self):
        factor = random.random()
        other = self.airfoil * factor
        self.assertAlmostEqual(other.thickness, self.airfoil.thickness * factor)
        other *= 1. / factor
        self.assertAlmostEqual(other.thickness, self.airfoil.thickness)

    def test_compute_naca(self):
        numpoints = random.randint(10, 200)
        thickness = random.randint(8, 20)
        m = random.randint(1, 9) * 1000  # Maximum camber position
        p = random.randint(1, 9) * 100  # Maximum thickness position
        prof = Airfoil.compute_naca(naca=m+p+thickness, numpoints=numpoints)
        self.assertAlmostEqual(prof.thickness*100, thickness, 0)

    def test_add(self):
        other = self.airfoil.copy()
        other = self.airfoil + other
        self.assertAlmostEqual(2*self.airfoil.thickness, other.thickness)

    def test_mul(self):
        self.airfoil *= 0
        self.assertAlmostEqual(self.airfoil.thickness, 0)

    def test_thickness(self):
        val = random.random()
        thickness = self.airfoil.thickness

        new = self.airfoil.set_thickness(thickness*val)

        self.assertAlmostEqual(new.thickness, thickness*val)

    def test_camber(self):
        val = random.random()
        camber_line = self.airfoil.camber_line
        camber = max([p[1] for p in camber_line])

        new = self.airfoil.set_camber(camber*val)

        self.assertAlmostEqual(new.camber, camber*val, places=3)
    
    def test_aoa(self):
        aoa = random.randrange(1,5)
        aoa = 10
        self.airfoil.xfoil_aoa(aoa)

    def test_polar(self):
        self.airfoil.xfoil_polar(-5, 15, 20)


if __name__ == '__main__':
    unittest.main(verbosity=2)
