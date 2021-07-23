# pyfoil

*A library to read, create, modify and analyse airfoils in Python*

## features

 * read `.dat` files
 * airfoil generators:
    * naca
    * joukowsky
    * treffz
    * vandevooren
    * web (selig db)
 * modify airfoils
    * resample
    * normalize
    * get points
    * get/set thickness
    * get/set camber
 * analyze airfoils (c++ xfoil lib included)

A major convention is that a local coordinate-system is ranging from x=-1 (upper back) towards the nose (x=0) towards the lower back (x=+1)


## example

**see [example.ipynb](example.ipynb)**