#! /bin/python

import pyfoil

foil = pyfoil.Airfoil.compute_naca(1222)
result=foil.get_polar(0, 20)

result["glide"] = result["cl"]/result["cd"]
print(result)

