import math

def compute_naca(naca: int, numpoints: int):

    """Compute and return a four-digit naca-airfoil"""
    # See: http://people.clarkson.edu/~pmarzocc/AE429/The%20NACA%20airfoil%20series.pdf
    # and: http://airfoiltools.com/airfoil/naca4digit
    m = int(naca / 1000) * 0.01  # Maximum Camber Position
    p = int((naca % 1000) / 100) * 0.1  # second digit: Maximum Thickness position
    t = (naca % 100) * 0.01  # last two digits: Maximum Thickness(%)
    x_values = [1-math.sin((x * 1. / (numpoints-1)) * math.pi / 2) for x in range(numpoints)]
    #x_values = self.cos_distribution(numpoints)

    upper = []
    lower = []
    a0 = 0.2969
    a1 = -0.126
    a2 = -0.3516
    a3 = 0.2843
    a4 = -0.1015

    for x in x_values:
        if x < p:
            mean_camber = (m / (p ** 2) * (2 * p * x - x ** 2))
            gradient = 2 * m / (p ** 2) * (p - x)
        else:
            mean_camber = (m / ((1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x - x ** 2))
            gradient = 2 * m / (1 - p ** 2) * (p - x)

        thickness_this = t / 0.2 * (a0 * math.sqrt(x) + a1 * x + a2 * x ** 2 + a3 * x ** 3 + a4 * x ** 4)
        #theta = math.atan(gradient)
        costheta = (1 + gradient ** 2) ** (-0.5)
        sintheta = gradient * costheta
        upper.append([x - thickness_this * sintheta,
                        mean_camber + thickness_this * costheta])
        lower.append([x + thickness_this * sintheta,
                        mean_camber - thickness_this * costheta])

    return upper + lower[::-1][1:]