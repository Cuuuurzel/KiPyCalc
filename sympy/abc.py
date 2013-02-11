from core import Symbol

# e, E, I, pi removed !!!

_latin = list('abcdefghijklmnopqrstuvwxyzABCDFGHJKLMNOPQRSTUVWXYZ')
# COSINEQ should not be imported as they clash; gamma, pi and zeta clash, too
_greek = 'alpha beta gamma delta epsilon zeta eta theta iota kappa '\
  'mu nu xi omicron rho sigma tau upsilon phi chi psi omega'.split(' ')

for _s in _latin + _greek:
    exec "%s = Symbol('%s')" % (_s, _s)

del _latin, _greek, _s
