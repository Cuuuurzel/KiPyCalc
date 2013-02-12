from core import Symbol

_latin = list('abcdefghijkloqrstvwxyzABCDFHJLNOQRSTUVWXYZ')
_greek = 'alpha beta gamma delta epsilon zeta eta theta iota kappa '\
  'mu nu xi omicron rho sigma tau upsilon phi chi psi omega'.split(' ')
_units = list( 'pnumKMGP' )

for _s in _latin + _greek + _units :
    exec "%s = Symbol('%s')" % (_s, _s)

del _latin, _greek, _s, _units
