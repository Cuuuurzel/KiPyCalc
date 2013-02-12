from sympy import I, symbols, sqrt, Add, Mul, Rational, Pow, Symbol, sympify, S
from sympy import Integer, conjugate, pretty, latex, oo, sin, pi, diff

from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.qexpr import QExpr
from sympy.physics.quantum.state import (
    Ket, Bra, TimeDepKet, TimeDepBra,
    KetBase, BraBase, StateBase, Wavefunction
)
from sympy.physics.quantum.hilbert import HilbertSpace
from sympy.utilities.pytest import raises

x,y,t = symbols('x,y,t')

class TestKet(Ket):
    @classmethod
    def default_args(self):
        return ("test",)

class TestKetMultipleLabels(Ket):
    @classmethod
    def default_args(self):
        return ("r", "theta", "phi")

class TestTimeDepKet(TimeDepKet):
    @classmethod
    def default_args(self):
        return ("test", "t")

class TestTimeDepKetMultipleLabels(TimeDepKet):
    @classmethod
    def default_args(self):
        return ("r", "theta", "phi", "t")

def test_ket():
    k = Ket('0')

    assert isinstance(k, Ket)
    assert isinstance(k, KetBase)
    assert isinstance(k, StateBase)
    assert isinstance(k, QExpr)

    assert k.label == (Symbol('0'),)
    assert k.hilbert_space == HilbertSpace()
    assert k.is_commutative == False

    # Make sure this doesn't get converted to the number pi.
    k = Ket('pi')
    assert k.label == (Symbol('pi'),)

    k = Ket(x,y)
    assert k.label == (x,y)
    assert k.hilbert_space == HilbertSpace()
    assert k.is_commutative == False

    assert k.dual_class() == Bra
    assert k.dual == Bra(x,y)
    assert k.subs(x,y) == Ket(y,y)

    k = TestKet()
    assert k == TestKet("test")

    k = TestKetMultipleLabels()
    assert k == TestKetMultipleLabels("r", "theta", "phi")

    assert Ket() == Ket('psi')


def test_bra():
    b = Bra('0')

    assert isinstance(b, Bra)
    assert isinstance(b, BraBase)
    assert isinstance(b, StateBase)
    assert isinstance(b, QExpr)

    assert b.label == (Symbol('0'),)
    assert b.hilbert_space == HilbertSpace()
    assert b.is_commutative == False

    # Make sure this doesn't get converted to the number pi.
    b = Bra('pi')
    assert b.label == (Symbol('pi'),)

    b = Bra(x,y)
    assert b.label == (x,y)
    assert b.hilbert_space == HilbertSpace()
    assert b.is_commutative == False

    assert b.dual_class() == Ket
    assert b.dual == Ket(x,y)
    assert b.subs(x,y) == Bra(y,y)

    assert Bra() == Bra('psi')

def test_ops():
    k0 = Ket(0)
    k1 = Ket(1)
    k = 2*I*k0 - (x/sqrt(2))*k1
    assert k == Add(Mul(2, I, k0),
        Mul(Rational(-1, 2), x, Pow(2, Rational(1, 2)), k1))


def test_time_dep_ket():
    k = TimeDepKet(0,t)

    assert isinstance(k, TimeDepKet)
    assert isinstance(k, KetBase)
    assert isinstance(k, StateBase)
    assert isinstance(k, QExpr)

    assert k.label == (Integer(0),)
    assert k.args == (Integer(0),t)
    assert k.time == t

    assert k.dual_class() == TimeDepBra
    assert k.dual == TimeDepBra(0,t)

    assert k.subs(t,2) == TimeDepKet(0,2)

    k = TimeDepKet(x, 0.5)
    assert k.label == (x,)
    assert k.args == (x,sympify(0.5))

    k = TestTimeDepKet()
    assert k.label == (Symbol("test"),)
    assert k.time == Symbol("t")
    assert k == TestTimeDepKet("test", "t")

    k = TestTimeDepKetMultipleLabels()
    assert k.label == (Symbol("r"), Symbol("theta"), Symbol("phi"))
    assert k.time == Symbol("t")
    assert k == TestTimeDepKetMultipleLabels("r", "theta", "phi", "t")

    assert TimeDepKet() == TimeDepKet("psi", "t")

def test_time_dep_bra():
    b = TimeDepBra(0,t)

    assert isinstance(b, TimeDepBra)
    assert isinstance(b, BraBase)
    assert isinstance(b, StateBase)
    assert isinstance(b, QExpr)

    assert b.label == (Integer(0),)
    assert b.args == (Integer(0),t)
    assert b.time == t

    assert b.dual_class() == TimeDepKet
    assert b.dual == TimeDepKet(0,t)

    k = TimeDepBra(x, 0.5)
    assert k.label == (x,)
    assert k.args == (x,sympify(0.5))

    assert TimeDepBra() == TimeDepBra("psi", "t")

def test_bra_ket_dagger():
    x = symbols('x',complex=True)
    k = Ket('k')
    b = Bra('b')
    assert Dagger(k) == Bra('k')
    assert Dagger(b) == Ket('b')
    assert Dagger(k).is_commutative == False

    k2 = Ket('k2')
    e = 2*I*k + x*k2
    assert Dagger(e) == conjugate(x)*Dagger(k2) - 2*I*Dagger(k)


def test_printing():
    psi = Ket('psi')
    assert pretty(psi, use_unicode=True) == u'\u2758\u03c8\u27e9'
    assert pretty(Dagger(psi), use_unicode=True) == u'\u27e8\u03c8\u2758'
    assert latex(psi) == r"{\left|\psi\right\rangle }"
    assert latex(Dagger(psi)) == r"{\left\langle \psi\right|}"

def test_wavefunction():
    x, L = symbols('x,L', real=True)
    n = symbols('n', integer=True)

    f = Wavefunction(x**2, x)
    p = f.prob()
    lims = f.limits

    assert f.is_normalized == False
    assert f.norm == oo
    assert f(10) == 100
    assert p(10) == 10000
    assert lims[x] == (-oo, oo)
    assert diff(f, x) == Wavefunction(2*x, x)
    raises(NotImplementedError, 'f.normalize()')
    assert conjugate(f) == Wavefunction(conjugate(f.expr), x)
    assert conjugate(f) == Dagger(f)

    g = Wavefunction(x**2*y+y**2*x, (x, 0, 1), (y, 0, 2))
    lims_g = g.limits

    assert lims_g[x] == (0, 1)
    assert lims_g[y] == (0, 2)
    assert g.is_normalized == False
    assert g.norm == sqrt(42)/3
    assert g(2,4) == 0
    assert g(1,1) == 2
    assert diff(diff(g, x), y) == Wavefunction(2*x + 2*y, (x, 0, 1), (y, 0, 2))
    assert conjugate(g) == Wavefunction(conjugate(g.expr), *g.args[1:])
    assert conjugate(g) == Dagger(g)

    h = Wavefunction(sqrt(5)*x**2, (x, 0, 1))
    assert h.is_normalized == True
    assert h.normalize() == h
    assert conjugate(h) == Wavefunction(conjugate(h.expr), (x, 0, 1))
    assert conjugate(h) == Dagger(h)

    piab = Wavefunction(sin(n*pi*x/L), (x, 0, L))
    assert piab.norm == sqrt(L/2)
    assert piab(L+1) == 0
    assert piab(0.5) == sin(0.5*n*pi/L)
    assert piab(0.5, n=1, L=1) == sin(0.5*pi)
    assert piab.normalize() == \
           Wavefunction(sqrt(2)/sqrt(L)*sin(n*pi*x/L), (x, 0, L))
    assert conjugate(piab) == Wavefunction(conjugate(piab.expr), (x, 0, L))
    assert conjugate(piab) == Dagger(piab)

    k = Wavefunction(x**2, 'x')
    assert type(k.variables[0]) == Symbol