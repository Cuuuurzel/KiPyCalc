from __future__ import print_function, division

from sympy.core.add import Add
from sympy.core.basic import C, sympify, cacheit
from sympy.core.singleton import S
from sympy.core.numbers import igcdex
from sympy.core.function import Function, ArgumentIndexError
from sympy.functions.elementary.miscellaneous import sqrt
from sympy.functions.elementary.exponential import log
from sympy.functions.elementary.hyperbolic import HyperbolicFunction
from sympy.utilities.iterables import numbered_symbols
from sympy.core.compatibility import xrange

###############################################################################
########################## TRIGONOMETRIC FUNCTIONS ############################
###############################################################################


class TrigonometricFunction(Function):
    """Base class for trigonometric functions. """

    unbranched = True

    def _eval_is_rational(self):
        s = self.func(*self.args)
        if s.func == self.func:
            if s.args[0].is_rational and s.args[0].is_nonzero:
                return False
        else:
            return s.is_rational

    def _eval_is_algebraic(self):
        s = self.func(*self.args)
        if s.func == self.func:
            if self.args[0].is_nonzero and self.args[0].is_algebraic:
                return False
            pi_coeff = _pi_coeff(self.args[0])
            if pi_coeff is not None and pi_coeff.is_rational:
                return True
        else:
            return s.is_algebraic

    def _eval_expand_complex(self, deep=True, **hints):
        re_part, im_part = self.as_real_imag(deep=deep, **hints)
        return re_part + im_part*S.ImaginaryUnit

    def _as_real_imag(self, deep=True, **hints):
        if self.args[0].is_real:
            if deep:
                hints['complex'] = False
                return (self.args[0].expand(deep, **hints), S.Zero)
            else:
                return (self.args[0], S.Zero)
        if deep:
            re, im = self.args[0].expand(deep, **hints).as_real_imag()
        else:
            re, im = self.args[0].as_real_imag()
        return (re, im)


def _peeloff_pi(arg):
    """
    Split ARG into two parts, a "rest" and a multiple of pi/2.
    This assumes ARG to be an Add.
    The multiple of pi returned in the second position is always a Rational.

    Examples:
    >>> from sympy.functions.elementary.trigonometric import _peeloff_pi as peel
    >>> from sympy import pi
    >>> from sympy.abc import x, y
    >>> peel(x + pi/2)
    (x, pi/2)
    >>> peel(x + 2*pi/3 + pi*y)
    (x + pi*y + pi/6, pi/2)
    """
    for a in Add.make_args(arg):
        if a is S.Pi:
            K = S.One
            break
        elif a.is_Mul:
            K, p = a.as_two_terms()
            if p is S.Pi and K.is_Rational:
                break
    else:
        return arg, S.Zero

    m1 = (K % S.Half) * S.Pi
    m2 = K*S.Pi - m1
    return arg - m2, m2


def _pi_coeff(arg, cycles=1):
    """
    When arg is a Number times pi (e.g. 3*pi/2) then return the Number
    normalized to be in the range [0, 2], else None.

    When an even multiple of pi is encountered, if it is multiplying
    something with known parity then the multiple is returned as 0 otherwise
    as 2.

    Examples
    ========

    >>> from sympy.functions.elementary.trigonometric import _pi_coeff as coeff
    >>> from sympy import pi, Dummy
    >>> from sympy.abc import x, y
    >>> coeff(3*x*pi)
    3*x
    >>> coeff(11*pi/7)
    11/7
    >>> coeff(-11*pi/7)
    3/7
    >>> coeff(4*pi)
    0
    >>> coeff(5*pi)
    1
    >>> coeff(5.0*pi)
    1
    >>> coeff(5.5*pi)
    3/2
    >>> coeff(2 + pi)

    >>> coeff(2*Dummy(integer=True)*pi)
    2
    >>> coeff(2*Dummy(even=True)*pi)
    0
    """
    arg = sympify(arg)
    if arg is S.Pi:
        return S.One
    elif not arg:
        return S.Zero
    elif arg.is_Mul:
        cx = arg.coeff(S.Pi)
        if cx:
            c, x = cx.as_coeff_Mul()  # pi is not included as coeff
            if c.is_Float:
                # recast exact binary fractions to Rationals
                f = abs(c) % 1
                if f != 0:
                    p = -int(round(log(f, 2).evalf()))
                    m = 2**p
                    cm = c*m
                    i = int(cm)
                    if i == cm:
                        c = C.Rational(i, m)
                        cx = c*x
                else:
                    c = C.Rational(int(c))
                    cx = c*x
            if x.is_integer:
                c2 = c % 2
                if c2 == 1:
                    return x
                elif not c2:
                    if x.is_even is not None:  # known parity
                        return S.Zero
                    return S(2)
                else:
                    return c2*x
            return cx


class sin(TrigonometricFunction):
    """
    The sine function.

    Returns the sine of x (measured in radians).

    Notes
    =====

    This function will evaluate automatically in the
    case x/pi is some rational number [4]_.  For example,
    if x is a multiple of pi, pi/2, pi/3, pi/4 and pi/6.

    Examples
    ========

    >>> from sympy import sin, pi
    >>> from sympy.abc import x
    >>> sin(x**2).diff(x)
    2*x*cos(x**2)
    >>> sin(1).diff(x)
    0
    >>> sin(pi)
    0
    >>> sin(pi/2)
    1
    >>> sin(pi/6)
    1/2

    See Also
    ========

    csc, cos, sec, tan, cot
    asin, acsc, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.14
    .. [3] http://functions.wolfram.com/ElementaryFunctions/Sin
    .. [4] http://mathworld.wolfram.com/TrigonometryAngles.html
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return cos(self.args[0])
        else:
            raise ArgumentIndexError(self, argindex)

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.Zero:
                return S.Zero
            elif arg is S.Infinity or arg is S.NegativeInfinity:
                return

        if arg.could_extract_minus_sign():
            return -cls(-arg)

        i_coeff = arg.as_coefficient(S.ImaginaryUnit)
        if i_coeff is not None:
            return S.ImaginaryUnit * C.sinh(i_coeff)

        pi_coeff = _pi_coeff(arg)
        if pi_coeff is not None:
            if pi_coeff.is_integer:
                return S.Zero

            if (2*pi_coeff).is_integer:
                if pi_coeff.is_even:
                    return S.Zero
                elif pi_coeff.is_even is False:
                    return S.NegativeOne**(pi_coeff - S.Half)

            if not pi_coeff.is_Rational:
                narg = pi_coeff*S.Pi
                if narg != arg:
                    return cls(narg)
                return None

            # https://github.com/sympy/sympy/issues/6048
            # transform a sine to a cosine, to avoid redundant code
            if pi_coeff.is_Rational:
                x = pi_coeff % 2
                if x > 1:
                    return -cls((x % 1)*S.Pi)
                if 2*x > 1:
                    return cls((1 - x)*S.Pi)
                narg = ((pi_coeff + C.Rational(3, 2)) % 2)*S.Pi
                result = cos(narg)
                if not isinstance(result, cos):
                    return result
                if pi_coeff*S.Pi != arg:
                    return cls(pi_coeff*S.Pi)
                return None

        if arg.is_Add:
            x, m = _peeloff_pi(arg)
            if m:
                return sin(m)*cos(x) + cos(m)*sin(x)

        if arg.func is asin:
            return arg.args[0]

        if arg.func is atan:
            x = arg.args[0]
            return x / sqrt(1 + x**2)

        if arg.func is atan2:
            y, x = arg.args
            return y / sqrt(x**2 + y**2)

        if arg.func is acos:
            x = arg.args[0]
            return sqrt(1 - x**2)

        if arg.func is acot:
            x = arg.args[0]
            return 1 / (sqrt(1 + 1 / x**2) * x)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)

            if len(previous_terms) > 2:
                p = previous_terms[-2]
                return -p * x**2 / (n*(n - 1))
            else:
                return (-1)**(n//2) * x**(n)/C.factorial(n)

    def _eval_rewrite_as_exp(self, arg):
        exp, I = C.exp, S.ImaginaryUnit
        if isinstance(arg, TrigonometricFunction) or isinstance(arg, HyperbolicFunction):
            arg = arg.func(arg.args[0]).rewrite(exp)
        return (exp(arg*I) - exp(-arg*I)) / (2*I)

    def _eval_rewrite_as_Pow(self, arg):
        if arg.func is log:
            I = S.ImaginaryUnit
            x = arg.args[0]
            return I*x**-I / 2 - I*x**I /2

    def _eval_rewrite_as_cos(self, arg):
        return -cos(arg + S.Pi/2)

    def _eval_rewrite_as_tan(self, arg):
        tan_half = tan(S.Half*arg)
        return 2*tan_half/(1 + tan_half**2)

    def _eval_rewrite_as_sincos(self, arg):
        return sin(arg)*cos(arg)/cos(arg)

    def _eval_rewrite_as_cot(self, arg):
        cot_half = cot(S.Half*arg)
        return 2*cot_half/(1 + cot_half**2)

    def _eval_rewrite_as_pow(self, arg):
        return self.rewrite(cos).rewrite(pow)

    def _eval_rewrite_as_sqrt(self, arg):
        return self.rewrite(cos).rewrite(sqrt)

    def _eval_rewrite_as_csc(self, arg):
        return 1/csc(arg)

    def _eval_conjugate(self):
        return self.func(self.args[0].conjugate())

    def as_real_imag(self, deep=True, **hints):
        re, im = self._as_real_imag(deep=deep, **hints)
        return (sin(re)*C.cosh(im), cos(re)*C.sinh(im))

    def _eval_expand_trig(self, **hints):
        from sympy import expand_mul
        arg = self.args[0]
        x = None
        if arg.is_Add:  # TODO, implement more if deep stuff here
            # TODO: Do this more efficiently for more than two terms
            x, y = arg.as_two_terms()
            sx = sin(x, evaluate=False)._eval_expand_trig()
            sy = sin(y, evaluate=False)._eval_expand_trig()
            cx = cos(x, evaluate=False)._eval_expand_trig()
            cy = cos(y, evaluate=False)._eval_expand_trig()
            return sx*cy + sy*cx
        else:
            n, x = arg.as_coeff_Mul(rational=True)
            if n.is_Integer:  # n will be positive because of .eval
                # canonicalization

                # See http://mathworld.wolfram.com/Multiple-AngleFormulas.html
                if n.is_odd:
                    return (-1)**((n - 1)/2)*C.chebyshevt(n, sin(x))
                else:
                    return expand_mul((-1)**(n/2 - 1)*cos(x)*C.chebyshevu(n -
                        1, sin(x)), deep=False)
            pi_coeff = _pi_coeff(arg)
            if pi_coeff is not None:
                if pi_coeff.is_Rational:
                    return self.rewrite(sqrt)
        return sin(arg)

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return arg
        else:
            return self.func(arg)

    def _eval_is_real(self):
        return self.args[0].is_real

    def _eval_is_finite(self):
        arg = self.args[0]
        if arg.is_real:
            return True

    def _sage_(self):
        import sage.all as sage
        return sage.sin(self.args[0]._sage_())


class cos(TrigonometricFunction):
    """
    The cosine function.

    Returns the cosine of x (measured in radians).

    Notes
    =====

    See :func:`sin` for notes about automatic evaluation.

    Examples
    ========

    >>> from sympy import cos, pi
    >>> from sympy.abc import x
    >>> cos(x**2).diff(x)
    -2*x*sin(x**2)
    >>> cos(1).diff(x)
    0
    >>> cos(pi)
    -1
    >>> cos(pi/2)
    0
    >>> cos(2*pi/3)
    -1/2

    See Also
    ========

    sin, csc, sec, tan, cot
    asin, acsc, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.14
    .. [3] http://functions.wolfram.com/ElementaryFunctions/Cos
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return -sin(self.args[0])
        else:
            raise ArgumentIndexError(self, argindex)

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.Zero:
                return S.One
            elif arg is S.Infinity or arg is S.NegativeInfinity:
                # In this cases, it is unclear if we should
                # return S.NaN or leave un-evaluated.  One
                # useful test case is how "limit(sin(x)/x,x,oo)"
                # is handled.
                # See test_sin_cos_with_infinity() an
                # Test for issue 3308
                # https://github.com/sympy/sympy/issues/5196
                # For now, we return un-evaluated.
                return

        if arg.could_extract_minus_sign():
            return cls(-arg)

        i_coeff = arg.as_coefficient(S.ImaginaryUnit)
        if i_coeff is not None:
            return C.cosh(i_coeff)

        pi_coeff = _pi_coeff(arg)
        if pi_coeff is not None:
            if pi_coeff.is_integer:
                return (S.NegativeOne)**pi_coeff

            if (2*pi_coeff).is_integer:
                if pi_coeff.is_even:
                    return (S.NegativeOne)**(pi_coeff/2)
                elif pi_coeff.is_even is False:
                    return S.Zero

            if not pi_coeff.is_Rational:
                narg = pi_coeff*S.Pi
                if narg != arg:
                    return cls(narg)
                return None

            # cosine formula #####################
            # https://github.com/sympy/sympy/issues/6048
            # explicit calculations are preformed for
            # cos(k pi / 8), cos(k pi /10), and cos(k pi / 12)
            # Some other exact values like cos(k pi/15) can be
            # calculated using a partial-fraction decomposition
            # by calling cos( X ).rewrite(sqrt)
            cst_table_some = {
                3: S.Half,
                5: (sqrt(5) + 1)/4,
            }
            if pi_coeff.is_Rational:
                q = pi_coeff.q
                p = pi_coeff.p % (2*q)
                if p > q:
                    narg = (pi_coeff - 1)*S.Pi
                    return -cls(narg)
                if 2*p > q:
                    narg = (1 - pi_coeff)*S.Pi
                    return -cls(narg)

                # If nested sqrt's are worse than un-evaluation
                # you can require q in (1, 2, 3, 4, 6)
                # q <= 12 returns expressions with 2 or fewer nestings.
                if q > 12:
                    return None

                if q in cst_table_some:
                    cts = cst_table_some[pi_coeff.q]
                    return C.chebyshevt(pi_coeff.p, cts).expand()

                if 0 == q % 2:
                    narg = (pi_coeff*2)*S.Pi
                    nval = cls(narg)
                    if None == nval:
                        return None
                    x = (2*pi_coeff + 1)/2
                    sign_cos = (-1)**((-1 if x < 0 else 1)*int(abs(x)))
                    return sign_cos*sqrt( (1 + nval)/2 )
            return None

        if arg.is_Add:
            x, m = _peeloff_pi(arg)
            if m:
                return cos(m)*cos(x) - sin(m)*sin(x)

        if arg.func is acos:
            return arg.args[0]

        if arg.func is atan:
            x = arg.args[0]
            return 1 / sqrt(1 + x**2)

        if arg.func is atan2:
            y, x = arg.args
            return x / sqrt(x**2 + y**2)

        if arg.func is asin:
            x = arg.args[0]
            return sqrt(1 - x ** 2)

        if arg.func is acot:
            x = arg.args[0]
            return 1 / sqrt(1 + 1 / x**2)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n < 0 or n % 2 == 1:
            return S.Zero
        else:
            x = sympify(x)

            if len(previous_terms) > 2:
                p = previous_terms[-2]
                return -p * x**2 / (n*(n - 1))
            else:
                return (-1)**(n//2)*x**(n)/C.factorial(n)

    def _eval_rewrite_as_exp(self, arg):
        exp, I = C.exp, S.ImaginaryUnit
        if isinstance(arg, TrigonometricFunction) or isinstance(arg, HyperbolicFunction):
            arg = arg.func(arg.args[0]).rewrite(exp)
        return (exp(arg*I) + exp(-arg*I)) / 2

    def _eval_rewrite_as_Pow(self, arg):
        if arg.func is log:
            I = S.ImaginaryUnit
            x = arg.args[0]
            return x**I/2 + x**-I/2

    def _eval_rewrite_as_sin(self, arg):
        return sin(arg + S.Pi/2)

    def _eval_rewrite_as_tan(self, arg):
        tan_half = tan(S.Half*arg)**2
        return (1 - tan_half)/(1 + tan_half)

    def _eval_rewrite_as_sincos(self, arg):
        return sin(arg)*cos(arg)/sin(arg)

    def _eval_rewrite_as_cot(self, arg):
        cot_half = cot(S.Half*arg)**2
        return (cot_half - 1)/(cot_half + 1)

    def _eval_rewrite_as_pow(self, arg):
        return self._eval_rewrite_as_sqrt(arg)

    def _eval_rewrite_as_sqrt(self, arg):

        def migcdex(x):
            # recursive calcuation of gcd and linear combination
            # for a sequence of integers.
            # Given  (x1, x2, x3)
            # Returns (y1, y1, y3, g)
            # such that g is the gcd and x1*y1+x2*y2+x3*y3 - g = 0
            # Note, that this is only one such linear combination.
            if len(x) == 1:
                return (1, x[0])
            if len(x) == 2:
                return igcdex(x[0], x[-1])
            g = migcdex(x[1:])
            u, v, h = igcdex(x[0], g[-1])
            return tuple([u] + [v*i for i in g[0:-1] ] + [h])

        def ipartfrac(r, factors=None):
            from sympy.ntheory import factorint
            if isinstance(r, int):
                return r
            if not isinstance(r, C.Rational):
                raise TypeError("r is not rational")
            n = r.q
            if 2 > r.q*r.q:
                return r.q

            if None == factors:
                a = [n//x**y for x, y in factorint(r.q).items()]
            else:
                a = [n//x for x in factors]
            if len(a) == 1:
                return [ r ]
            h = migcdex(a)
            ans = [ r.p*C.Rational(i*j, r.q) for i, j in zip(h[:-1], a) ]
            assert r == sum(ans)
            return ans
        pi_coeff = _pi_coeff(arg)
        if pi_coeff is None:
            return None

        assert not pi_coeff.is_integer, "should have been simplified already"

        if not pi_coeff.is_Rational:
            return None

        cst_table_some = {
            3: S.Half,
            5: (sqrt(5) + 1)/4,
            17: sqrt((15 + sqrt(17))/32 + sqrt(2)*(sqrt(17 - sqrt(17)) +
                sqrt(sqrt(2)*(-8*sqrt(17 + sqrt(17)) - (1 - sqrt(17))
                *sqrt(17 - sqrt(17))) + 6*sqrt(17) + 34))/32)
            # 65537 and 257 are the only other known Fermat primes
            # Please add if you would like them
        }

        def fermatCoords(n):
            if not isinstance(n, int):
                raise TypeError("n is not an integer")
            if n <= 0:
                raise ValueError("n has to be greater than 0")
            if n == 1 or 0 == n % 2:
                return False
            primes = dict( [(p, 0) for p in cst_table_some ] )
            assert 1 not in primes
            for p_i in primes:
                while 0 == n % p_i:
                    n = n/p_i
                    primes[p_i] += 1
            if 1 != n:
                return False
            if max(primes.values()) > 1:
                return False
            return tuple([ p for p in primes if primes[p] == 1])

        if pi_coeff.q in cst_table_some:
            return C.chebyshevt(pi_coeff.p, cst_table_some[pi_coeff.q]).expand()

        if 0 == pi_coeff.q % 2:  # recursively remove powers of 2
            narg = (pi_coeff*2)*S.Pi
            nval = cos(narg)
            if None == nval:
                return None
            nval = nval.rewrite(sqrt)
            x = (2*pi_coeff + 1)/2
            sign_cos = (-1)**((-1 if x < 0 else 1)*int(abs(x)))
            return sign_cos*sqrt( (1 + nval)/2 )

        FC = fermatCoords(pi_coeff.q)
        if FC:
            decomp = ipartfrac(pi_coeff, FC)
            X = [(x[1], x[0]*S.Pi) for x in zip(decomp, numbered_symbols('z'))]
            pcls = cos(sum([x[0] for x in X]))._eval_expand_trig().subs(X)
            return pcls.rewrite(sqrt)
        else:
            decomp = ipartfrac(pi_coeff)
            X = [(x[1], x[0]*S.Pi) for x in zip(decomp, numbered_symbols('z'))]
            pcls = cos(sum([x[0] for x in X]))._eval_expand_trig().subs(X)
            return pcls

    def _eval_rewrite_as_sec(self, arg):
        return 1/sec(arg)

    def _eval_conjugate(self):
        return self.func(self.args[0].conjugate())

    def as_real_imag(self, deep=True, **hints):
        re, im = self._as_real_imag(deep=deep, **hints)
        return (cos(re)*C.cosh(im), -sin(re)*C.sinh(im))

    def _eval_expand_trig(self, **hints):
        arg = self.args[0]
        x = None
        if arg.is_Add:  # TODO: Do this more efficiently for more than two terms
            x, y = arg.as_two_terms()
            sx = sin(x, evaluate=False)._eval_expand_trig()
            sy = sin(y, evaluate=False)._eval_expand_trig()
            cx = cos(x, evaluate=False)._eval_expand_trig()
            cy = cos(y, evaluate=False)._eval_expand_trig()
            return cx*cy - sx*sy
        else:
            coeff, terms = arg.as_coeff_Mul(rational=True)
            if coeff.is_Integer:
                return C.chebyshevt(coeff, cos(terms))
            pi_coeff = _pi_coeff(arg)
            if pi_coeff is not None:
                if pi_coeff.is_Rational:
                    return self.rewrite(sqrt)
        return cos(arg)

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return S.One
        else:
            return self.func(arg)

    def _eval_is_real(self):
        return self.args[0].is_real

    def _eval_is_finite(self):
        arg = self.args[0]

        if arg.is_real:
            return True

    def _sage_(self):
        import sage.all as sage
        return sage.cos(self.args[0]._sage_())


class tan(TrigonometricFunction):
    """
    The tangent function.

    Returns the tangent of x (measured in radians).

    Notes
    =====

    See :func:`sin` for notes about automatic evaluation.

    Examples
    ========

    >>> from sympy import tan
    >>> from sympy.abc import x
    >>> tan(x**2).diff(x)
    2*x*(tan(x**2)**2 + 1)
    >>> tan(1).diff(x)
    0

    See Also
    ========

    sin, csc, cos, sec, cot
    asin, acsc, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.14
    .. [3] http://functions.wolfram.com/ElementaryFunctions/Tan
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return S.One + self**2
        else:
            raise ArgumentIndexError(self, argindex)

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return atan

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.Zero:
                return S.Zero

        if arg.could_extract_minus_sign():
            return -cls(-arg)

        i_coeff = arg.as_coefficient(S.ImaginaryUnit)
        if i_coeff is not None:
            return S.ImaginaryUnit * C.tanh(i_coeff)

        pi_coeff = _pi_coeff(arg, 2)
        if pi_coeff is not None:
            if pi_coeff.is_integer:
                return S.Zero

            if not pi_coeff.is_Rational:
                narg = pi_coeff*S.Pi
                if narg != arg:
                    return cls(narg)
                return None

            if pi_coeff.is_Rational:
                narg = ((pi_coeff + S.Half) % 1 - S.Half)*S.Pi
                # see cos() to specify which expressions should  be
                # expanded automatically in terms of radicals
                cresult, sresult = cos(narg), cos(narg - S.Pi/2)
                if not isinstance(cresult, cos) \
                        and not isinstance(sresult, cos):
                    if cresult == 0:
                        return S.ComplexInfinity
                    return (sresult/cresult)
                if narg != arg:
                    return cls(narg)

        if arg.is_Add:
            x, m = _peeloff_pi(arg)
            if m:
                tanm = tan(m)
                tanx = tan(x)
                if tanm is S.ComplexInfinity:
                    return -cot(x)
                return (tanm + tanx)/(1 - tanm*tanx)

        if arg.func is atan:
            return arg.args[0]

        if arg.func is atan2:
            y, x = arg.args
            return y/x

        if arg.func is asin:
            x = arg.args[0]
            return x / sqrt(1 - x**2)

        if arg.func is acos:
            x = arg.args[0]
            return sqrt(1 - x**2) / x

        if arg.func is acot:
            x = arg.args[0]
            return 1 / x

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)

            a, b = ((n - 1)//2), 2**(n + 1)

            B = C.bernoulli(n + 1)
            F = C.factorial(n + 1)

            return (-1)**a * b*(b - 1) * B/F * x**n

    def _eval_nseries(self, x, n, logx):
        i = self.args[0].limit(x, 0)*2/S.Pi
        if i and i.is_Integer:
            return self.rewrite(cos)._eval_nseries(x, n=n, logx=logx)
        return Function._eval_nseries(self, x, n=n, logx=logx)

    def _eval_rewrite_as_Pow(self, arg):
        if arg.func is log:
            I = S.ImaginaryUnit
            x = arg.args[0]
            return I*(x**-I - x**I)/(x**-I + x**I)

    def _eval_conjugate(self):
        return self.func(self.args[0].conjugate())

    def as_real_imag(self, deep=True, **hints):
        re, im = self._as_real_imag(deep=deep, **hints)
        if im:
            denom = cos(2*re) + C.cosh(2*im)
            return (sin(2*re)/denom, C.sinh(2*im)/denom)
        else:
            return (self.func(re), S.Zero)

    def _eval_expand_trig(self, **hints):
        arg = self.args[0]
        x = None
        if arg.is_Add:
            from sympy import symmetric_poly
            n = len(arg.args)
            TX = []
            for x in arg.args:
                tx = tan(x, evaluate=False)._eval_expand_trig()
                TX.append(tx)

            Yg = numbered_symbols('Y')
            Y = [ next(Yg) for i in xrange(n) ]

            p = [0, 0]
            for i in xrange(n + 1):
                p[1 - i % 2] += symmetric_poly(i, Y)*(-1)**((i % 4)//2)
            return (p[0]/p[1]).subs(list(zip(Y, TX)))

        else:
            coeff, terms = arg.as_coeff_Mul(rational=True)
            if coeff.is_Integer and coeff > 1:
                I = S.ImaginaryUnit
                z = C.Symbol('dummy', real=True)
                P = ((1 + I*z)**coeff).expand()
                return (C.im(P)/C.re(P)).subs([(z, tan(terms))])
        return tan(arg)

    def _eval_rewrite_as_exp(self, arg):
        exp, I = C.exp, S.ImaginaryUnit
        if isinstance(arg, TrigonometricFunction) or isinstance(arg, HyperbolicFunction):
            arg = arg.func(arg.args[0]).rewrite(exp)
        neg_exp, pos_exp = exp(-arg*I), exp(arg*I)
        return I*(neg_exp - pos_exp)/(neg_exp + pos_exp)

    def _eval_rewrite_as_sin(self, x):
        return 2*sin(x)**2/sin(2*x)

    def _eval_rewrite_as_cos(self, x):
        return -cos(x + S.Pi/2)/cos(x)

    def _eval_rewrite_as_sincos(self, arg):
        return sin(arg)/cos(arg)

    def _eval_rewrite_as_cot(self, arg):
        return 1/cot(arg)

    def _eval_rewrite_as_pow(self, arg):
        y = self.rewrite(cos).rewrite(pow)
        if y.has(cos):
            return None
        return y

    def _eval_rewrite_as_sqrt(self, arg):
        y = self.rewrite(cos).rewrite(sqrt)
        if y.has(cos):
            return None
        return y

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return arg
        else:
            return self.func(arg)

    def _eval_is_real(self):
        return self.args[0].is_real

    def _eval_is_finite(self):
        arg = self.args[0]

        if arg.is_imaginary:
            return True

    def _sage_(self):
        import sage.all as sage
        return sage.tan(self.args[0]._sage_())


class cot(TrigonometricFunction):
    """
    The cotangent function.

    Returns the cotangent of x (measured in radians).

    Notes
    =====

    See :func:`sin` for notes about automatic evaluation.

    Examples
    ========

    >>> from sympy import cot
    >>> from sympy.abc import x
    >>> cot(x**2).diff(x)
    2*x*(-cot(x**2)**2 - 1)
    >>> cot(1).diff(x)
    0

    See Also
    ========

    sin, csc, cos, sec, tan
    asin, acsc, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.14
    .. [3] http://functions.wolfram.com/ElementaryFunctions/Cot
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return S.NegativeOne - self**2
        else:
            raise ArgumentIndexError(self, argindex)

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return acot

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            if arg is S.Zero:
                return S.ComplexInfinity

        if arg.could_extract_minus_sign():
            return -cls(-arg)

        i_coeff = arg.as_coefficient(S.ImaginaryUnit)
        if i_coeff is not None:
            return -S.ImaginaryUnit * C.coth(i_coeff)

        pi_coeff = _pi_coeff(arg, 2)
        if pi_coeff is not None:
            if pi_coeff.is_integer:
                return S.ComplexInfinity

            if not pi_coeff.is_Rational:
                narg = pi_coeff*S.Pi
                if narg != arg:
                    return cls(narg)
                return None

            if pi_coeff.is_Rational:
                narg = (((pi_coeff + S.Half) % 1) - S.Half)*S.Pi
                # see cos() to specify which expressions should be
                # expanded automatically in terms of radicals
                cresult, sresult = cos(narg), cos(narg - S.Pi/2)
                if not isinstance(cresult, cos) \
                        and not isinstance(sresult, cos):
                    if sresult == 0:
                        return S.ComplexInfinity
                    return cresult / sresult
                if narg != arg:
                    return cls(narg)

        if arg.is_Add:
            x, m = _peeloff_pi(arg)
            if m:
                cotm = cot(m)
                if cotm == 0:
                    return -tan(x)
                cotx = cot(x)
                if cotm is S.ComplexInfinity:
                    return cotx
                if cotm.is_Rational:
                    return (cotm*cotx - 1) / (cotm + cotx)
            return None

        if arg.func is acot:
            return arg.args[0]

        if arg.func is atan:
            x = arg.args[0]
            return 1 / x

        if arg.func is atan2:
            y, x = arg.args
            return x/y

        if arg.func is asin:
            x = arg.args[0]
            return sqrt(1 - x**2) / x

        if arg.func is acos:
            x = arg.args[0]
            return x / sqrt(1 - x**2)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n == 0:
            return 1 / sympify(x)
        elif n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)

            B = C.bernoulli(n + 1)
            F = C.factorial(n + 1)

            return (-1)**((n + 1)//2) * 2**(n + 1) * B/F * x**n

    def _eval_nseries(self, x, n, logx):
        i = self.args[0].limit(x, 0)/S.Pi
        if i and i.is_Integer:
            return self.rewrite(cos)._eval_nseries(x, n=n, logx=logx)
        return self.rewrite(tan)._eval_nseries(x, n=n, logx=logx)

    def _eval_conjugate(self):
        return self.func(self.args[0].conjugate())

    def as_real_imag(self, deep=True, **hints):
        re, im = self._as_real_imag(deep=deep, **hints)
        if im:
            denom = cos(2*re) - C.cosh(2*im)
            return (-sin(2*re)/denom, -C.sinh(2*im)/denom)
        else:
            return (self.func(re), S.Zero)

    def _eval_rewrite_as_exp(self, arg):
        exp, I = C.exp, S.ImaginaryUnit
        if isinstance(arg, TrigonometricFunction) or isinstance(arg, HyperbolicFunction):
            arg = arg.func(arg.args[0]).rewrite(exp)
        neg_exp, pos_exp = exp(-arg*I), exp(arg*I)
        return I*(pos_exp + neg_exp)/(pos_exp - neg_exp)

    def _eval_rewrite_as_Pow(self, arg):
        if arg.func is log:
            I = S.ImaginaryUnit
            x = arg.args[0]
            return -I*(x**-I + x**I)/(x**-I - x**I)

    def _eval_rewrite_as_sin(self, x):
        return 2*sin(2*x)/sin(x)**2

    def _eval_rewrite_as_cos(self, x):
        return -cos(x)/cos(x + S.Pi/2)

    def _eval_rewrite_as_sincos(self, arg):
        return cos(arg)/sin(arg)

    def _eval_rewrite_as_tan(self, arg):
        return 1/tan(arg)

    def _eval_rewrite_as_pow(self, arg):
        y = self.rewrite(cos).rewrite(pow)
        if y.has(cos):
            return None
        return y

    def _eval_rewrite_as_sqrt(self, arg):
        y = self.rewrite(cos).rewrite(sqrt)
        if y.has(cos):
            return None
        return y

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return 1/arg
        else:
            return self.func(arg)

    def _eval_is_real(self):
        return self.args[0].is_real

    def _eval_expand_trig(self, **hints):
        arg = self.args[0]
        x = None
        if arg.is_Add:
            from sympy import symmetric_poly
            n = len(arg.args)
            CX = []
            for x in arg.args:
                cx = cot(x, evaluate=False)._eval_expand_trig()
                CX.append(cx)

            Yg = numbered_symbols('Y')
            Y = [ next(Yg) for i in xrange(n) ]

            p = [0, 0]
            for i in xrange(n, -1, -1):
                p[(n - i) % 2] += symmetric_poly(i, Y)*(-1)**(((n - i) % 4)//2)
            return (p[0]/p[1]).subs(list(zip(Y, CX)))
        else:
            coeff, terms = arg.as_coeff_Mul(rational=True)
            if coeff.is_Integer and coeff > 1:
                I = S.ImaginaryUnit
                z = C.Symbol('dummy', real=True)
                P = ((z + I)**coeff).expand()
                return (C.re(P)/C.im(P)).subs([(z, cot(terms))])
        return cot(arg)

    def _eval_is_finite(self):
        arg = self.args[0]
        if arg.is_imaginary:
            return True

    def _eval_subs(self, old, new):
        if self == old:
            return new
        arg = self.args[0]
        argnew = arg.subs(old, new)
        if arg != argnew and (argnew/S.Pi).is_integer:
            return S.ComplexInfinity
        return cot(argnew)

    def _sage_(self):
        import sage.all as sage
        return sage.cot(self.args[0]._sage_())


class ReciprocalTrigonometricFunction(TrigonometricFunction):
    """Base class for reciprocal functions of trigonometric functions. """

    _reciprocal_of = None       # mandatory, to be defined in subclass

    # _is_even and _is_odd are used for correct evaluation of csc(-x), sec(-x)
    # TODO refactor into TrigonometricFunction common parts of
    # trigonometric functions eval() like even/odd, func(x+2*k*pi), etc.
    _is_even = None  # optional, to be defined in subclass
    _is_odd = None   # optional, to be defined in subclass

    @classmethod
    def eval(cls, arg):
        if arg.could_extract_minus_sign():
            if cls._is_even:
                return cls(-arg)
            if cls._is_odd:
                return -cls(-arg)

        pi_coeff = _pi_coeff(arg)
        if (pi_coeff is not None
            and not (2*pi_coeff).is_integer
            and pi_coeff.is_Rational):
                q = pi_coeff.q
                p = pi_coeff.p % (2*q)
                if p > q:
                    narg = (pi_coeff - 1)*S.Pi
                    return -cls(narg)
                if 2*p > q:
                    narg = (1 - pi_coeff)*S.Pi
                    if cls._is_odd:
                        return cls(narg)
                    elif cls._is_even:
                        return -cls(narg)

        t = cls._reciprocal_of.eval(arg)
        if hasattr(arg, 'inverse') and arg.inverse() == cls:
            return arg.args[0]
        return 1/t if t != None else t

    def _call_reciprocal(self, method_name, *args, **kwargs):
        # Calls method_name on _reciprocal_of
        o = self._reciprocal_of(self.args[0])
        return getattr(o, method_name)(*args, **kwargs)

    def _calculate_reciprocal(self, method_name, *args, **kwargs):
        # If calling method_name on _reciprocal_of returns a value != None
        # then return the reciprocal of that value
        t = self._call_reciprocal(method_name, *args, **kwargs)
        return 1/t if t != None else t

    def _rewrite_reciprocal(self, method_name, arg):
        # Special handling for rewrite functions. If reciprocal rewrite returns
        # unmodified expression, then return None
        t = self._call_reciprocal(method_name, arg)
        if t != None and t != self._reciprocal_of(arg):
            return 1/t

    def fdiff(self, argindex=1):
        return -self._calculate_reciprocal("fdiff", argindex)/self**2

    def _eval_rewrite_as_exp(self, arg):
        return self._rewrite_reciprocal("_eval_rewrite_as_exp", arg)

    def _eval_rewrite_as_Pow(self, arg):
        return self._rewrite_reciprocal("_eval_rewrite_as_Pow", arg)

    def _eval_rewrite_as_sin(self, arg):
        return self._rewrite_reciprocal("_eval_rewrite_as_sin", arg)

    def _eval_rewrite_as_cos(self, arg):
        return self._rewrite_reciprocal("_eval_rewrite_as_cos", arg)

    def _eval_rewrite_as_tan(self, arg):
        return self._rewrite_reciprocal("_eval_rewrite_as_tan", arg)

    def _eval_rewrite_as_pow(self, arg):
        return self._rewrite_reciprocal("_eval_rewrite_as_pow", arg)

    def _eval_rewrite_as_sqrt(self, arg):
        return self._rewrite_reciprocal("_eval_rewrite_as_sqrt", arg)

    def _eval_conjugate(self):
        return self.func(self.args[0].conjugate())

    def as_real_imag(self, deep=True, **hints):
        return (1/self._reciprocal_of(self.args[0])).as_real_imag(deep,
                                                                  **hints)

    def _eval_expand_trig(self, **hints):
        return self._calculate_reciprocal("_eval_expand_trig", **hints)

    def _eval_is_real(self):
        return self._reciprocal_of(self.args[0])._eval_is_real()

    def _eval_as_leading_term(self, x):
        return (1/self._reciprocal_of(self.args[0]))._eval_as_leading_term(x)

    def _eval_is_finite(self):
        return (1/self._reciprocal_of(self.args[0])).is_finite

    def _eval_nseries(self, x, n, logx):
        return (1/self._reciprocal_of(self.args[0]))._eval_nseries(x, n, logx)


class sec(ReciprocalTrigonometricFunction):
    """
    The secant function.

    Returns the secant of x (measured in radians).

    Notes
    =====

    See :func:`sin` for notes about automatic evaluation.

    Examples
    ========

    >>> from sympy import sec
    >>> from sympy.abc import x
    >>> sec(x**2).diff(x)
    2*x*tan(x**2)*sec(x**2)
    >>> sec(1).diff(x)
    0

    See Also
    ========

    sin, csc, cos, tan, cot
    asin, acsc, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.14
    .. [2] http://functions.wolfram.com/ElementaryFunctions/Sec
    """

    _reciprocal_of = cos
    _is_even = True

    def _eval_rewrite_as_cot(self, arg):
        cot_half_sq = cot(arg/2)**2
        return (cot_half_sq + 1)/(cot_half_sq - 1)

    def _eval_rewrite_as_cos(self, arg):
        return (1/cos(arg))

    def _eval_rewrite_as_sincos(self, arg):
        return sin(arg)/(cos(arg)*sin(arg))

    def fdiff(self, argindex=1):
        if argindex == 1:
            return tan(self.args[0])*sec(self.args[0])
        else:
            raise ArgumentIndexError(self, argindex)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        # Reference Formula:
        # http://functions.wolfram.com/ElementaryFunctions/Sec/06/01/02/01/
        if n < 0 or n % 2 == 1:
            return S.Zero
        else:
            x = sympify(x)
            k = n//2
            return (-1)**k*C.euler(2*k)/C.factorial(2*k)*x**(2*k)

    def _sage_(self):
        import sage.all as sage
        return sage.sec(self.args[0]._sage_())


class csc(ReciprocalTrigonometricFunction):
    """
    The cosecant function.

    Returns the cosecant of x (measured in radians).

    Notes
    =====

    See :func:`sin` for notes about automatic evaluation.

    Examples
    ========

    >>> from sympy import csc
    >>> from sympy.abc import x
    >>> csc(x**2).diff(x)
    -2*x*cot(x**2)*csc(x**2)
    >>> csc(1).diff(x)
    0

    See Also
    ========

    sin, cos, sec, tan, cot
    asin, acsc, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.14
    .. [3] http://functions.wolfram.com/ElementaryFunctions/Csc
    """

    _reciprocal_of = sin
    _is_odd = True

    def _eval_rewrite_as_sin(self, arg):
        return (1/sin(arg))

    def _eval_rewrite_as_sincos(self, arg):
        return cos(arg)/(sin(arg)*cos(arg))

    def _eval_rewrite_as_cot(self, arg):
        cot_half = cot(arg/2)
        return (1 + cot_half**2)/(2*cot_half)

    def fdiff(self, argindex=1):
        if argindex == 1:
            return -cot(self.args[0])*csc(self.args[0])
        else:
            raise ArgumentIndexError(self, argindex)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n == 0:
            return 1/sympify(x)
        elif n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)
            k = n//2 + 1
            return ((-1)**(k - 1)*2*(2**(2*k - 1) - 1)*
                    C.bernoulli(2*k)*x**(2*k - 1)/C.factorial(2*k))

    def _sage_(self):
        import sage.all as sage
        return sage.csc(self.args[0]._sage_())


###############################################################################
########################### TRIGONOMETRIC INVERSES ############################
###############################################################################


class InverseTrigonometricFunction(Function):
    """Base class for inverse trigonometric functions."""

    pass


class asin(InverseTrigonometricFunction):
    """
    The inverse sine function.

    Returns the arcsine of x in radians.

    Notes
    =====

    asin(x) will evaluate automatically in the cases oo, -oo, 0, 1,
    -1 and for some instances when the result is a rational multiple
    of pi (see the eval class method).

    Examples
    ========

    >>> from sympy import asin, oo, pi
    >>> asin(1)
    pi/2
    >>> asin(-1)
    -pi/2

    See Also
    ========

    sin, csc, cos, sec, tan, cot
    acsc, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.23
    .. [3] http://functions.wolfram.com/ElementaryFunctions/ArcSin
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return 1/sqrt(1 - self.args[0]**2)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_is_rational(self):
        s = self.func(*self.args)
        if s.func == self.func:
            if s.args[0].is_rational:
                return False
        else:
            return s.is_rational

    def _eval_is_positive(self):
        if self.args[0].is_positive:
            return (self.args[0] - 1).is_negative
        if self.args[0].is_negative:
            return not (self.args[0] + 1).is_positive

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.Infinity:
                return S.NegativeInfinity * S.ImaginaryUnit
            elif arg is S.NegativeInfinity:
                return S.Infinity * S.ImaginaryUnit
            elif arg is S.Zero:
                return S.Zero
            elif arg is S.One:
                return S.Pi / 2
            elif arg is S.NegativeOne:
                return -S.Pi / 2

        if arg.could_extract_minus_sign():
            return -cls(-arg)

        if arg.is_number:
            cst_table = {
                sqrt(3)/2: 3,
                -sqrt(3)/2: -3,
                sqrt(2)/2: 4,
                -sqrt(2)/2: -4,
                1/sqrt(2): 4,
                -1/sqrt(2): -4,
                sqrt((5 - sqrt(5))/8): 5,
                -sqrt((5 - sqrt(5))/8): -5,
                S.Half: 6,
                -S.Half: -6,
                sqrt(2 - sqrt(2))/2: 8,
                -sqrt(2 - sqrt(2))/2: -8,
                (sqrt(5) - 1)/4: 10,
                (1 - sqrt(5))/4: -10,
                (sqrt(3) - 1)/sqrt(2**3): 12,
                (1 - sqrt(3))/sqrt(2**3): -12,
                (sqrt(5) + 1)/4: S(10)/3,
                -(sqrt(5) + 1)/4: -S(10)/3
            }

            if arg in cst_table:
                return S.Pi / cst_table[arg]

        i_coeff = arg.as_coefficient(S.ImaginaryUnit)
        if i_coeff is not None:
            return S.ImaginaryUnit * C.asinh(i_coeff)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)
            if len(previous_terms) >= 2 and n > 2:
                p = previous_terms[-2]
                return p * (n - 2)**2/(n*(n - 1)) * x**2
            else:
                k = (n - 1) // 2
                R = C.RisingFactorial(S.Half, k)
                F = C.factorial(k)
                return R / F * x**n / n

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return arg
        else:
            return self.func(arg)

    def _eval_rewrite_as_acos(self, x):
        return S.Pi/2 - acos(x)

    def _eval_rewrite_as_atan(self, x):
        return 2*atan(x/(1 + sqrt(1 - x**2)))

    def _eval_rewrite_as_log(self, x):
        return -S.ImaginaryUnit*C.log(S.ImaginaryUnit*x + sqrt(1 - x**2))

    def _eval_rewrite_as_acot(self, arg):
        return 2*acot((1 + sqrt(1 - arg**2))/arg)

    def _eval_rewrite_as_asec(self, arg):
        return S.Pi/2 - asec(1/arg)

    def _eval_rewrite_as_acsc(self, arg):
        return acsc(1/arg)

    def _eval_is_real(self):
        x = self.args[0]
        return x.is_real and (1 - abs(x)).is_nonnegative

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return sin

    def _sage_(self):
        import sage.all as sage
        return sage.asin(self.args[0]._sage_())


class acos(InverseTrigonometricFunction):
    """
    The inverse cosine function.

    Returns the arc cosine of x (measured in radians).

    Notes
    =====

    acos(x) will evaluate automatically in the cases
    oo, -oo, 0, 1, -1.

    Examples
    ========

    >>> from sympy import acos, oo, pi
    >>> acos(1)
    0
    >>> acos(0)
    pi/2
    >>> acos(oo)
    oo*I

    See Also
    ========

    sin, csc, cos, sec, tan, cot
    asin, acsc, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.23
    .. [3] http://functions.wolfram.com/ElementaryFunctions/ArcCos
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return -1/sqrt(1 - self.args[0]**2)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_is_rational(self):
        s = self.func(*self.args)
        if s.func == self.func:
            if s.args[0].is_rational:
                return False
        else:
            return s.is_rational

    def _eval_is_positive(self):
        x = self.args[0]
        return (1 - abs(x)).is_nonnegative

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.Infinity:
                return S.Infinity * S.ImaginaryUnit
            elif arg is S.NegativeInfinity:
                return S.NegativeInfinity * S.ImaginaryUnit
            elif arg is S.Zero:
                return S.Pi / 2
            elif arg is S.One:
                return S.Zero
            elif arg is S.NegativeOne:
                return S.Pi

        if arg.is_number:
            cst_table = {
                S.Half: S.Pi/3,
                -S.Half: 2*S.Pi/3,
                sqrt(2)/2: S.Pi/4,
                -sqrt(2)/2: 3*S.Pi/4,
                1/sqrt(2): S.Pi/4,
                -1/sqrt(2): 3*S.Pi/4,
                sqrt(3)/2: S.Pi/6,
                -sqrt(3)/2: 5*S.Pi/6,
            }

            if arg in cst_table:
                return cst_table[arg]

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n == 0:
            return S.Pi / 2
        elif n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)
            if len(previous_terms) >= 2 and n > 2:
                p = previous_terms[-2]
                return p * (n - 2)**2/(n*(n - 1)) * x**2
            else:
                k = (n - 1) // 2
                R = C.RisingFactorial(S.Half, k)
                F = C.factorial(k)
                return -R / F * x**n / n

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return arg
        else:
            return self.func(arg)

    def _eval_is_real(self):
        x = self.args[0]
        return x.is_real and (1 - abs(x)).is_nonnegative

    def _eval_rewrite_as_log(self, x):
        return S.Pi/2 + S.ImaginaryUnit * \
            C.log(S.ImaginaryUnit * x + sqrt(1 - x**2))

    def _eval_rewrite_as_asin(self, x):
        return S.Pi/2 - asin(x)

    def _eval_rewrite_as_atan(self, x):
        return atan(sqrt(1 - x**2)/x) + (S.Pi/2)*(1 - x*sqrt(1/x**2))

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return cos

    def _eval_rewrite_as_acot(self, arg):
        return S.Pi/2 - 2*acot((1 + sqrt(1 - arg**2))/arg)

    def _eval_rewrite_as_asec(self, arg):
        return asec(1/arg)

    def _eval_rewrite_as_acsc(self, arg):
        return S.Pi/2 - acsc(1/arg)

    def _eval_conjugate(self):
        z = self.args[0]
        r = self.func(self.args[0].conjugate())
        if z.is_real is False:
            return r
        elif z.is_real and (z + 1).is_nonnegative and (z - 1).is_nonpositive:
            return r

    def _sage_(self):
        import sage.all as sage
        return sage.acos(self.args[0]._sage_())


class atan(InverseTrigonometricFunction):
    """
    The inverse tangent function.

    Returns the arc tangent of x (measured in radians).

    Notes
    =====

    atan(x) will evaluate automatically in the cases
    oo, -oo, 0, 1, -1.

    Examples
    ========

    >>> from sympy import atan, oo, pi
    >>> atan(0)
    0
    >>> atan(1)
    pi/4
    >>> atan(oo)
    pi/2

    See Also
    ========

    sin, csc, cos, sec, tan, cot
    asin, acsc, acos, asec, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.23
    .. [3] http://functions.wolfram.com/ElementaryFunctions/ArcTan
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return 1/(1 + self.args[0]**2)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_is_rational(self):
        s = self.func(*self.args)
        if s.func == self.func:
            if s.args[0].is_rational:
                return False
        else:
            return s.is_rational

    def _eval_is_positive(self):
        return self.args[0].is_positive

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.Infinity:
                return S.Pi / 2
            elif arg is S.NegativeInfinity:
                return -S.Pi / 2
            elif arg is S.Zero:
                return S.Zero
            elif arg is S.One:
                return S.Pi / 4
            elif arg is S.NegativeOne:
                return -S.Pi / 4
        if arg.could_extract_minus_sign():
            return -cls(-arg)

        if arg.is_number:
            cst_table = {
                sqrt(3)/3: 6,
                -sqrt(3)/3: -6,
                1/sqrt(3): 6,
                -1/sqrt(3): -6,
                sqrt(3): 3,
                -sqrt(3): -3,
                (1 + sqrt(2)): S(8)/3,
                -(1 + sqrt(2)): S(8)/3,
                (sqrt(2) - 1): 8,
                (1 - sqrt(2)): -8,
                sqrt((5 + 2*sqrt(5))): S(5)/2,
                -sqrt((5 + 2*sqrt(5))): -S(5)/2,
                (2 - sqrt(3)): 12,
                -(2 - sqrt(3)): -12
            }

            if arg in cst_table:
                return S.Pi / cst_table[arg]

        i_coeff = arg.as_coefficient(S.ImaginaryUnit)
        if i_coeff is not None:
            return S.ImaginaryUnit * C.atanh(i_coeff)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)
            return (-1)**((n - 1)//2) * x**n / n

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return arg
        else:
            return self.func(arg)

    def _eval_is_real(self):
        return self.args[0].is_real

    def _eval_rewrite_as_log(self, x):
        return S.ImaginaryUnit/2 * (C.log(
            (S(1) - S.ImaginaryUnit * x)/(S(1) + S.ImaginaryUnit * x)))

    def _eval_aseries(self, n, args0, x, logx):
        if args0[0] == S.Infinity:
            return (S.Pi/2 - atan(1/self.args[0]))._eval_nseries(x, n, logx)
        elif args0[0] == S.NegativeInfinity:
            return (-S.Pi/2 - atan(1/self.args[0]))._eval_nseries(x, n, logx)
        else:
            return super(atan, self)._eval_aseries(n, args0, x, logx)

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return tan

    def _eval_rewrite_as_asin(self, arg):
        return sqrt(arg**2)/arg*(S.Pi/2 - asin(1/sqrt(1 + arg**2)))

    def _eval_rewrite_as_acos(self, arg):
        return sqrt(arg**2)/arg*acos(1/sqrt(1 + arg**2))

    def _eval_rewrite_as_acot(self, arg):
        return acot(1/arg)

    def _eval_rewrite_as_asec(self, arg):
        return sqrt(arg**2)/arg*asec(sqrt(1 + arg**2))

    def _eval_rewrite_as_acsc(self, arg):
        return sqrt(arg**2)/arg*(S.Pi/2 - acsc(sqrt(1 + arg**2)))

    def _sage_(self):
        import sage.all as sage
        return sage.atan(self.args[0]._sage_())


class acot(InverseTrigonometricFunction):
    """
    The inverse cotangent function.

    Returns the arc cotangent of x (measured in radians).

    See Also
    ========

    sin, csc, cos, sec, tan, cot
    asin, acsc, acos, asec, atan, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.23
    .. [3] http://functions.wolfram.com/ElementaryFunctions/ArcCot
    """

    def fdiff(self, argindex=1):
        if argindex == 1:
            return -1 / (1 + self.args[0]**2)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_is_rational(self):
        s = self.func(*self.args)
        if s.func == self.func:
            if s.args[0].is_rational:
                return False
        else:
            return s.is_rational

    def _eval_is_positive(self):
        return self.args[0].is_real

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.Infinity:
                return S.Zero
            elif arg is S.NegativeInfinity:
                return S.Zero
            elif arg is S.Zero:
                return S.Pi/ 2
            elif arg is S.One:
                return S.Pi / 4
            elif arg is S.NegativeOne:
                return -S.Pi / 4

        if arg.could_extract_minus_sign():
            return -cls(-arg)

        if arg.is_number:
            cst_table = {
                sqrt(3)/3: 3,
                -sqrt(3)/3: -3,
                1/sqrt(3): 3,
                -1/sqrt(3): -3,
                sqrt(3): 6,
                -sqrt(3): -6,
                (1 + sqrt(2)): 8,
                -(1 + sqrt(2)): -8,
                (1 - sqrt(2)): -S(8)/3,
                (sqrt(2) - 1): S(8)/3,
                sqrt(5 + 2*sqrt(5)): 10,
                -sqrt(5 + 2*sqrt(5)): -10,
                (2 + sqrt(3)): 12,
                -(2 + sqrt(3)): -12,
                (2 - sqrt(3)): S(12)/5,
                -(2 - sqrt(3)): -S(12)/5,
            }

            if arg in cst_table:
                return S.Pi / cst_table[arg]

        i_coeff = arg.as_coefficient(S.ImaginaryUnit)
        if i_coeff is not None:
            return -S.ImaginaryUnit * C.acoth(i_coeff)

    @staticmethod
    @cacheit
    def taylor_term(n, x, *previous_terms):
        if n == 0:
            return S.Pi / 2  # FIX THIS
        elif n < 0 or n % 2 == 0:
            return S.Zero
        else:
            x = sympify(x)
            return (-1)**((n + 1)//2) * x**n / n

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)

        if x in arg.free_symbols and C.Order(1, x).contains(arg):
            return arg
        else:
            return self.func(arg)

    def _eval_is_real(self):
        return self.args[0].is_real

    def _eval_aseries(self, n, args0, x, logx):
        if args0[0] == S.Infinity:
            return (S.Pi/2 - acot(1/self.args[0]))._eval_nseries(x, n, logx)
        elif args0[0] == S.NegativeInfinity:
            return (3*S.Pi/2 - acot(1/self.args[0]))._eval_nseries(x, n, logx)
        else:
            return super(atan, self)._eval_aseries(n, args0, x, logx)

    def _eval_rewrite_as_log(self, x):
        return S.ImaginaryUnit/2 * \
            (C.log((x - S.ImaginaryUnit)/(x + S.ImaginaryUnit)))

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return cot

    def _eval_rewrite_as_asin(self, arg):
        return (arg*sqrt(1/arg**2)*
                (S.Pi/2 - asin(sqrt(-arg**2)/sqrt(-arg**2 - 1))))

    def _eval_rewrite_as_acos(self, arg):
        return arg*sqrt(1/arg**2)*acos(sqrt(-arg**2)/sqrt(-arg**2 - 1))

    def _eval_rewrite_as_atan(self, arg):
        return atan(1/arg)

    def _eval_rewrite_as_asec(self, arg):
        return arg*sqrt(1/arg**2)*asec(sqrt((1 + arg**2)/arg**2))

    def _eval_rewrite_as_acsc(self, arg):
        return arg*sqrt(1/arg**2)*(S.Pi/2 - acsc(sqrt((1 + arg**2)/arg**2)))

    def _sage_(self):
        import sage.all as sage
        return sage.acot(self.args[0]._sage_())


class asec(InverseTrigonometricFunction):
    """
    The inverse secant function.

    Returns the arc secant of x (measured in radians).

    Notes
    =====

    asec(x) will evaluate automatically in the cases
    oo, -oo, 0, 1, -1.

    Examples
    ========

    >>> from sympy import asec, oo, pi
    >>> asec(1)
    0
    >>> asec(-1)
    pi

    See Also
    ========

    sin, csc, cos, sec, tan, cot
    asin, acsc, acos, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.23
    .. [3] http://functions.wolfram.com/ElementaryFunctions/ArcSec
    """

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.One:
                return S.Zero
            elif arg is S.NegativeOne:
                return S.Pi
        if arg in [S.Infinity, S.NegativeInfinity, S.ComplexInfinity]:
            return S.Pi/2

    def fdiff(self, argindex=1):
        if argindex == 1:
            return 1/(self.args[0]**2*sqrt(1 - 1/self.args[0]**2))
        else:
            raise ArgumentIndexError(self, argindex)

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return sec

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)
        if C.Order(1,x).contains(arg):
            return C.log(arg)
        else:
            return self.func(arg)

    def _eval_rewrite_as_log(self, arg):
        return S.Pi/2 + S.ImaginaryUnit*C.log(S.ImaginaryUnit/arg + sqrt(1 - 1/arg**2))

    def _eval_rewrite_as_asin(self, arg):
        return S.Pi/2 - asin(1/arg)

    def _eval_rewrite_as_acos(self, arg):
        return acos(1/arg)

    def _eval_rewrite_as_atan(self, arg):
        return sqrt(arg**2)/arg*(-S.Pi/2 + 2*atan(arg + sqrt(arg**2 - 1)))

    def _eval_rewrite_as_acot(self, arg):
        return sqrt(arg**2)/arg*(-S.Pi/2 + 2*acot(arg - sqrt(arg**2 - 1)))

    def _eval_rewrite_as_acsc(self, arg):
        return S.Pi/2 - acsc(arg)

    def _sage_(self):
        import sage.all as sage
        return sage.arcsec(self.args[0]._sage_())


class acsc(InverseTrigonometricFunction):
    """
    The inverse cosecant function.

    Returns the arc cosecant of x (measured in radians).

    Notes
    =====

    acsc(x) will evaluate automatically in the cases
    oo, -oo, 0, 1, -1.

    Examples
    ========

    >>> from sympy import acsc, oo, pi
    >>> acsc(1)
    pi/2
    >>> acsc(-1)
    -pi/2

    See Also
    ========

    sin, csc, cos, sec, tan, cot
    asin, acos, asec, atan, acot, atan2

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    .. [2] http://dlmf.nist.gov/4.23
    .. [3] http://functions.wolfram.com/ElementaryFunctions/ArcCsc
    """

    @classmethod
    def eval(cls, arg):
        if arg.is_Number:
            if arg is S.NaN:
                return S.NaN
            elif arg is S.One:
                return S.Pi/2
            elif arg is S.NegativeOne:
                return -S.Pi/2
        if arg in [S.Infinity, S.NegativeInfinity, S.ComplexInfinity]:
            return S.Zero

    def fdiff(self, argindex=1):
        if argindex == 1:
            return -1/(self.args[0]**2*sqrt(1 - 1/self.args[0]**2))
        else:
            raise ArgumentIndexError(self, argindex)

    def inverse(self, argindex=1):
        """
        Returns the inverse of this function.
        """
        return csc

    def _eval_as_leading_term(self, x):
        arg = self.args[0].as_leading_term(x)
        if C.Order(1,x).contains(arg):
            return C.log(arg)
        else:
            return self.func(arg)

    def _eval_rewrite_as_log(self, arg):
        return -S.ImaginaryUnit*C.log(S.ImaginaryUnit/arg + sqrt(1 - 1/arg**2))

    def _eval_rewrite_as_asin(self, arg):
        return asin(1/arg)

    def _eval_rewrite_as_acos(self, arg):
        return S.Pi/2 - acos(1/arg)

    def _eval_rewrite_as_atan(self, arg):
        return sqrt(arg**2)/arg*(S.Pi/2 - atan(sqrt(arg**2 - 1)))

    def _eval_rewrite_as_acot(self, arg):
        return sqrt(arg**2)/arg*(S.Pi/2 - acot(1/sqrt(arg**2 - 1)))

    def _eval_rewrite_as_asec(self, arg):
        return S.Pi/2 - asec(arg)

    def _sage_(self):
        import sage.all as sage
        return sage.arccsc(self.args[0]._sage_())


class atan2(InverseTrigonometricFunction):
    r"""
    The function ``atan2(y, x)`` computes `\operatorname{atan}(y/x)` taking
    two arguments `y` and `x`.  Signs of both `y` and `x` are considered to
    determine the appropriate quadrant of `\operatorname{atan}(y/x)`.
    The range is `(-\pi, \pi]`. The complete definition reads as follows:

    .. math::

        \operatorname{atan2}(y, x) =
        \begin{cases}
          \arctan\left(\frac y x\right) & \qquad x > 0 \\
          \arctan\left(\frac y x\right) + \pi& \qquad y \ge 0 , x < 0 \\
          \arctan\left(\frac y x\right) - \pi& \qquad y < 0 , x < 0 \\
          +\frac{\pi}{2} & \qquad y > 0 , x = 0 \\
          -\frac{\pi}{2} & \qquad y < 0 , x = 0 \\
          \text{undefined} & \qquad y = 0, x = 0
        \end{cases}

    Attention: Note the role reversal of both arguments. The `y`-coordinate
    is the first argument and the `x`-coordinate the second.

    Examples
    ========

    Going counter-clock wise around the origin we find the
    following angles:

    >>> from sympy import atan2
    >>> atan2(0, 1)
    0
    >>> atan2(1, 1)
    pi/4
    >>> atan2(1, 0)
    pi/2
    >>> atan2(1, -1)
    3*pi/4
    >>> atan2(0, -1)
    pi
    >>> atan2(-1, -1)
    -3*pi/4
    >>> atan2(-1, 0)
    -pi/2
    >>> atan2(-1, 1)
    -pi/4

    which are all correct. Compare this to the results of the ordinary
    `\operatorname{atan}` function for the point `(x, y) = (-1, 1)`

    >>> from sympy import atan, S
    >>> atan(S(1) / -1)
    -pi/4
    >>> atan2(1, -1)
    3*pi/4

    where only the `\operatorname{atan2}` function reurns what we expect.
    We can differentiate the function with respect to both arguments:

    >>> from sympy import diff
    >>> from sympy.abc import x, y
    >>> diff(atan2(y, x), x)
    -y/(x**2 + y**2)

    >>> diff(atan2(y, x), y)
    x/(x**2 + y**2)

    We can express the `\operatorname{atan2}` function in terms of
    complex logarithms:

    >>> from sympy import log
    >>> atan2(y, x).rewrite(log)
    -I*log((x + I*y)/sqrt(x**2 + y**2))

    and in terms of `\operatorname(atan)`:

    >>> from sympy import atan
    >>> atan2(y, x).rewrite(atan)
    2*atan(y/(x + sqrt(x**2 + y**2)))

    but note that this form is undefined on the negative real axis.

    See Also
    ========

    sin, csc, cos, sec, tan, cot
    asin, acsc, acos, asec, atan, acot

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    .. [2] http://en.wikipedia.org/wiki/Atan2
    .. [3] http://functions.wolfram.com/ElementaryFunctions/ArcTan2
    """

    @classmethod
    def eval(cls, y, x):
        if x is S.NegativeInfinity:
            if y.is_zero:
                # Special case y = 0 because we define Heaviside(0) = 1/2
                return S.Pi
            return 2*S.Pi*(C.Heaviside(C.re(y))) - S.Pi
        elif x is S.Infinity:
            return S.Zero
        elif x.is_imaginary and y.is_imaginary and x.is_number and y.is_number:
            x = C.im(x)
            y = C.im(y)

        if x.is_real and y.is_real:
            if x.is_positive:
                return atan(y / x)
            elif x.is_negative:
                if y.is_negative:
                    return atan(y / x) - S.Pi
                elif y.is_nonnegative:
                    return atan(y / x) + S.Pi
            elif x.is_zero:
                if y.is_positive:
                    return S.Pi/2
                elif y.is_negative:
                    return -S.Pi/2
                elif y.is_zero:
                    return S.NaN
        if y.is_zero and x.is_real and x.is_nonzero:
            return S.Pi * (S.One - C.Heaviside(x))
        if x.is_number and y.is_number:
            return -S.ImaginaryUnit*C.log(
                (x + S.ImaginaryUnit*y)/sqrt(x**2 + y**2))

    def _eval_rewrite_as_log(self, y, x):
        return -S.ImaginaryUnit*C.log((x + S.ImaginaryUnit*y) / sqrt(x**2 + y**2))

    def _eval_rewrite_as_atan(self, y, x):
        return 2*atan(y / (sqrt(x**2 + y**2) + x))

    def _eval_rewrite_as_arg(self, y, x):
        if x.is_real and y.is_real:
            return C.arg(x + y*S.ImaginaryUnit)
        I = S.ImaginaryUnit
        n = x + I*y
        d = x**2 + y**2
        return C.arg(n/sqrt(d)) - I*log(abs(n)/sqrt(abs(d)))

    def _eval_is_real(self):
        return self.args[0].is_real and self.args[1].is_real

    def _eval_conjugate(self):
        return self.func(self.args[0].conjugate(), self.args[1].conjugate())

    def fdiff(self, argindex):
        y, x = self.args
        if argindex == 1:
            # Diff wrt y
            return x/(x**2 + y**2)
        elif argindex == 2:
            # Diff wrt x
            return -y/(x**2 + y**2)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_evalf(self, prec):
        y, x = self.args
        if x.is_real and y.is_real:
            super(atan2, self)._eval_evalf(prec)

    def _sage_(self):
        import sage.all as sage
        return sage.atan2(self.args[0]._sage_(), self.args[1]._sage_())
