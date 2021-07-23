# pyfoil

*A library to read, create, modify and analyse airfoils in Python*

## features

 * read `.dat` files
 * create naca-airfoils
 * create joukowsky, treffz, vandevooren airfoils
 * modify airfoils
    * resample
    * normalize
 * analyze airfoils (c++ xfoil lib included)


## example

``` python
import pyfoil

airfoil = pyfoil.Airfoil.compute_naca(3315).normalized()
airfoil.resample(50).numpoints
>51

airfoil.solver.ncrit = 9.
airfoil.xfoil(5, degree=True)
>cl	0.77906
>cd	0.00837475
>cdp	0.00239627
>cm	-0.041238
>xtr_top	0.267372
>xtr_bottom	0.5
>reynolds	2e+06
>converged	1



```