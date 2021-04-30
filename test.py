#! /bin/python

import openglider.airfoil as foil
import xfoil

solver = xfoil.Solver()
airfoil = foil.Profile2D.compute_naca(1234)

solver.load(airfoil.curve.tolist())
solver.run_aoa([x*3.141/180 for x in range(0, 10)])
