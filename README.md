KiPyCalc Pro
============

This branch of my project KiPyCalc has a completely different plotter.
My goal is to feed the plotter with iterable objects.
For example :
[ x**3 -4*x, x**3 -4*x +1, x**3 -4*x +2, x**3 -4*x +3 ]
or, less trivially :
map( lambda f,i:f+i, range(0,3), [x**3 -4*x]*3 )


This app is also available on the Play Store.
