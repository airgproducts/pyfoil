from typing import List
import os
import re
import math
import logging
import xml.etree.ElementTree as XMLTree

import euklid
import xfoil
import pandas

from pyfoil.generators import JoukowskyAirfoil, VanDeVoorenAirfoil, TrefftzKuttaAirfoil, compute_naca


logger = logging.getLogger(__name__)

solver = xfoil.Solver()

class Airfoil:
    noseindex: int
    name: str
    
    ncrit = 4
    xtr_top = 0.5
    xtr_bottom = 0.5

    
    def __init__(self, data, name="unnamed") -> None:
        self.name = name
        self.curve = euklid.vector.PolyLine2D(data)

        self._setup()

    def _setup(self):
        i = 0
        data = self.curve.nodes
        while data[i + 1][0] < data[i][0] and i < len(data):
            i += 1
        self.noseindex = i

        # Create a mapping x -> ik value
        self._interpolation_x_values = euklid.vector.Interpolation(
            [[-p[0], i] for i, p in enumerate(self.curve.nodes[:self.noseindex])] +
            [[ p[0], i+self.noseindex] for i, p in enumerate(self.curve.nodes[self.noseindex:])]
        )

    def _load_xfoil(self):
        solver.ncrit = self.ncrit
        solver.xtr_top = self.xtr_top
        solver.xtr_bottom = self.xtr_bottom

        if len(self.curve) > 300:
            raise Exception(f"too many numpoints for profile {self.name}: {len(self.curve)}")
        
        solver.load(self.curve.tolist())

    
    def xfoil_aoa(self, aoa: float, degree=True, load=True) -> xfoil.Result:
        # TODO: reynolds
        if degree:
            aoa = aoa * math.pi / 180

        if load:
            self._load_xfoil()

        return solver.run_aoa(aoa)
    
    def xfoil_polar(self, aoa_start, aoa_end, steps=10, degree=True) -> pandas.DataFrame:
        self._load_xfoil()
        delta = (aoa_end-aoa_start)/(steps-1)
        data = []
        for i in range(steps):
            aoa = aoa_start + delta*i

            try:
                result = self.xfoil_aoa(aoa, degree=degree, load=False)
            except RuntimeError:
                continue

            if result.converged:
                data.append([
                    result.aoa,
                    result.cl,
                    result.cd,
                    result.cdp,
                    result.cm
                ])
        
        return pandas.DataFrame(data, columns=["aoa", "cl", "cd", "cdp", "cm"])


    def __mul__(self, value) -> "Airfoil":
        fakt = euklid.vector.Vector2D([1, float(value)])

        return Airfoil(self.curve * fakt)

    def __call__(self, xval) -> float:
        return self.get_ik(xval)

    def get_ik(self, x) -> float:
        xval = float(x)
        return self._interpolation_x_values.get_value(xval)
    
    def get(self, x) -> euklid.vector.Vector2D:
        ik = self.get_ik(x)
        return self.curve.get(ik)

    def align(self, p) -> euklid.vector.Vector2D:
        """Align a point (x, y) on the airfoil. x: (0,1), y: (-1,1)"""
        x, y = p

        upper = self.get(-x)
        lower = self.get(x)

        return lower + (upper-lower) * ((y + 1)/2)

    def profilepoint(self, xval, h=-1.) -> euklid.vector.Vector2D:
        """
        Get airfoil Point for x-value (<0:upper side)
        optional: height (-1:lower,1:upper)
        """
        if h == -1:
            return self.get(xval)
        else:
            return self.align([xval, h])

    def normalized(self, close=True) -> "Airfoil":
        """
        Normalize the airfoil.
        This routine does:
            *Put the nose back to (0,0)
            *De-rotate airfoil
            *Reset its length to 1
        """
        nose = self.curve.nodes[self.noseindex]

        new_curve: euklid.vector.PolyLine2D = self.curve.move(nose * -1)

        diff = (new_curve.nodes[0] + new_curve.nodes[-1]) * 0.5

        # normalize length
        new_curve = new_curve.scale(1/diff.length())

        # de-rotate
        rotation = euklid.vector.Rotation2D(-diff.angle())
        new_nodes = [rotation.apply(p) for p in new_curve.nodes]

        if close:
            new_nodes[0][1] = 0
            new_nodes[-1][1] = 0
        
        return Airfoil(new_nodes)
    
    @property
    def normvectors(self) -> euklid.vector.PolyLine2D:
        return self.curve.normvectors()

    def __deepcopy__(self, memo):
        cpy = self.copy()
        memo[id(self)] = cpy
        return cpy

    def __copy__(self):
        return self.copy()

    def copy(self) -> "Airfoil":
        return Airfoil(self.curve.nodes, self.name)

    def __add__(self, other, conservative=False) -> "Airfoil":
        """
        Mix 2 Profiles
        """
        new = []
        for i, point in enumerate(self.curve.nodes):
            x = point[0]
            if i < self.noseindex:
                x = -x

            y2 = other.get(x)[1]
            new.append(point + [0, y2])
        
        return Airfoil(new)

    def __json__(self):
        return {
            "data": [list(p) for p in self.curve.nodes],
            "name": self.name
        }

    _re_number = r"([-+]?\d*\.\d*(?:[eE][+-]?\d+)?|\d+)"
    _re_coord_line = re.compile(rf"\s*{_re_number}\s+{_re_number}\s*")

    @classmethod
    def import_from_dat(cls, path) -> "Airfoil":
        """
        Import an airfoil from a '.dat' file
        """
        name = os.path.split(path)[-1]
        with open(path, "r") as p_file:
            return cls._import_dat(p_file, name=name)
    
    @classmethod
    def _import_dat(cls, p_file, name="unnamed") -> "Airfoil":
        profile = []
        for i, line in enumerate(p_file):
            if line.endswith(","):
                line = line[:-1]

            match = cls._re_coord_line.match(line)

            if match:
                profile.append([float(i) for i in match.groups()])
            elif i == 0:
                name = line.strip()
            elif len(line) == 0:
                continue
            else:
                logger.error(f"error in dat airfoil: {name} {i}:({line.strip()})")

        return cls(profile, name)


    def export_dat(self, pfad) -> str:
        """
        Export airfoil to .dat Format
        """
        with open(pfad, "w") as out:
            if self.name:
                out.write(str(self.name).strip())
            for p in self.curve.nodes:
                out.write("\n{: 10.8f}\t{: 10.8f}".format(*p))
        return pfad

    #@cached_property('self')
    @property
    def x_values(self) -> List[float]:
        """Get XValues of airfoil. upper side neg, lower positive"""
        i = self.noseindex

        x_values = [-vector[0] for vector in self.curve.nodes[:i]]
        x_values += [vector[0] for vector in self.curve.nodes[i:]]
        return x_values

    def set_x_values(self, xval) -> "Airfoil":
        """Set X-Values of airfoil to defined points."""
        new_nodes = [
            self.get(x) for x in xval
        ]

        return Airfoil(new_nodes)

    @property
    def numpoints(self) -> int:
        return len(self.curve.nodes)

    def resample(self, numpoints) -> "Airfoil":
        numpoints -= numpoints % 2  # brauchts?

        xtemp = lambda x: ((x > 0.5) - (x < 0.5)) * (1 - math.sin(math.pi * x))

        x_values = ([xtemp(i/numpoints) for i in range(numpoints+1)])

        return self.set_x_values(x_values)

    @property
    def thickness(self):
        """return the maximum sickness (Sic!) of an airfoil"""
        xvals = sorted(set(map(abs, self.x_values)))

        return max([
            abs(self.get(-x)[1] - self.get(x)[1]) for x in xvals
        ])

    def set_thickness(self, newthick):
        factor = float(newthick / self.thickness)

        name = self.name
        if name is not None:
            name += "_" + str(newthick) + "%"

        return Airfoil(self.curve * [1, factor])

    @property
    def camber_line(self) -> euklid.vector.Interpolation:
        xvals = sorted(set(map(abs, self.x_values)))
        return euklid.vector.Interpolation([self.profilepoint(i, 0.) for i in xvals])

    #@cached_property('self')
    @property
    def camber(self):
        """return the maximum camber of the airfoil"""
        return max([p[1] for p in self.camber_line])

    def set_camber(self, newcamber) -> "Airfoil":
        """Set maximal camber to the new value"""
        old_camber = self.camber
        factor = newcamber / old_camber - 1
        old_camber_line = self.camber_line

        data = [p + [0, old_camber_line.get_value(p[0]) * factor] for p in self.curve.nodes]

        return Airfoil(data)

    def insert_point(self, pos, tolerance=1e-5) -> "Airfoil":
        nearest_x_value = self.find_nearest_x_value(pos)
        new_nodes = self.curve.nodes[:]

        if abs(nearest_x_value - pos) > tolerance:
            point = self.get(pos)
            ik = self.get_ik(pos)

            new_nodes.insert(int(ik + 1), point)

        return Airfoil(new_nodes)

    def remove_points(self, start, end, tolerance=0.) -> "Airfoil":
        new_data = []

        ik_start = self.get_ik(start)
        ik_end = self.get_ik(end)

        i_start = int(ik_start - ik_start%1)
        if (self.curve.get(ik_start)-self.curve.get(i_start)).length() > tolerance:
            i_start += 1
        
        i_end = int(ik_end - ik_end%1)
        if (self.curve.get(ik_end)-self.curve.get(i_end+1)).length() <= tolerance:
            i_end += 1

        new_data = self.curve.nodes[:i_start+1] + self.curve.nodes[i_end:]
        
        return Airfoil(new_data)

    def move_nearest_point(self, pos) -> "Airfoil":
        ik = self(pos)
        diff = ik % 1.
        if diff < 0.5:
            i = int(ik)
        else:
            i = int(ik)+1

        new_nodes = self.curve.nodes[:i-1]
        new_nodes.append(self.profilepoint(pos))
        new_nodes += self.curve.nodes[i:]

        return Airfoil(new_nodes)

    def find_nearest_x_value(self, x: float) -> float:
        ik = self.get_ik(x)

        diff = ik % 1.
        if diff < 0.5:
            i = int(ik)
        else:
            i = int(ik)+1
        
        result = self.curve.get(i)[0]

        if x < 0:
            result = -result
        return result

    def apply_function(self, foo):
        self.curve = euklid.vector.PolyLine2D(
            [foo(p, upper=i<self.noseindex) for i, p in enumerate(self.curve.nodes)]
        )

    @classmethod
    def fetch(cls, name='atr72sm', base_url='http://m-selig.ae.illinois.edu/ads/coord/{name}.dat') -> "Airfoil":
        import urllib.request
        
        with urllib.request.urlopen(base_url.format(name=name)) as data_file:
            dat_str = data_file.read().decode('utf8')
            return cls._import_dat(dat_str.split("\n"))

    def add_flap(self, flap_begin, flap_amount) -> "Airfoil":
        
        def f(x, a, b):
            c1, c2, c3 = -a**2*b/(a**2 - 2*a + 1), 2*a*b/(a**2 - 2*a + 1), -b/(a**2 - 2*a + 1)
            if x < a:
                return 0.
            if x > 1:
                return -b
            return c1 + c2 * x + c3 * x**2
        
        new_nodes = []

        for p in self.curve.nodes:
            dy = f(abs(p[0]), flap_begin, flap_amount)
            new_nodes.append(euklid.vector.Vector2D([p[0], p[1]+dy]))
        
        return Airfoil(new_nodes, self.name+"_flap")

    @classmethod
    def compute_naca(cls, naca=1234, numpoints=100) -> "Airfoil":
        nodes = compute_naca(naca, numpoints)
        return cls(nodes, name=f"NACA_{naca:04d}").normalized()

    @classmethod
    def compute_trefftz(cls, m=-0.1+0.1j, tau=0.05, numpoints=100) -> "Airfoil":
        airfoil = TrefftzKuttaAirfoil(midpoint=m, tau=tau)

        # find the smallest xvalue to reset the nose
        profile = cls(airfoil.coordinates(numpoints), f"TrefftzKuttaAirfoil_m={m}_tau={tau}")
        return profile.normalized()

    @classmethod
    def compute_joukowsky(cls, m=-0.1+0.1j, numpoints=100) -> "Airfoil":
        airfoil = JoukowskyAirfoil(m)

        profile = cls(airfoil.coordinates(numpoints), f"joukowsky_{m}")
        return profile.normalized().resample(numpoints)

    @classmethod
    def compute_vandevooren(cls, tau=0.05, epsilon=0.05, numpoints=100) -> "Airfoil":
        airfoil = VanDeVoorenAirfoil(tau=tau, epsilon=epsilon)

        profile = cls(airfoil.coordinates(numpoints), f"VanDeVooren_tau={tau}_epsilon={epsilon}")        
        return profile.normalized()
    
    def _repr_svg_(self) -> str:
        result = '<svg baseProfile="full" height="100%" version="1.1" viewBox="-0.1,-0.25,1.2,0.5" width="100%" xmlns="http://www.w3.org/2000/svg">\n'
        result += """<defs><style type="text/css">
            line { vector-effect: non-scaling-stroke; stroke-width: 1; fill: none}
            polyline { vector-effect: non-scaling-stroke; stroke-width: 1; fill: none}
        </style></defs>"""

        result += '<g transform="scale(1,-1)">'
        result += '<polyline stroke="black" stroke-width="0.25" points="'

        for p in self.curve.nodes:
            result += f"{p[0]},{p[1]} "
        
        result = result[:-1] + '"></polyline>'

        result += '<polyline stroke="red" stroke-width="0.25" points="'

        for p in self.camber_line.nodes:
            result += f"{p[0]},{p[1]} "
        
        result = result[:-1] + '"></polyline>'

        result += '</g></svg>'

        return result
