from .field import FQ, bn128_Field
from .utils import log2, mul_scalar

class FieldPolynomial:
    field = None
    def __init__(self):
        if self.field is None:
            raise AttributeError("Field hasn't been specified")
        self.s = 1
        self.t = self.field.field_modulus - self.s

        while self.t % 2 != 1:
            self.s = self.s + 1
            self.t = self.t >> 1

        rem = self.t
        s = self.s - 1

        self.w = { s : bn128_Field(5)**rem }
        self.wi = { s :  bn128_Field(1) / self.w[s] }

        n = s - 1
        while n >= 0:
            self.w.update({n : self.w[n+1]**2})
            self.wi.update({n : self.wi[n+1]**2})
            n -= 1

        self.roots = {}
        self._set_roots(15)

    def _set_roots(self, n: int):
        self.roots = {}
        for i in reversed(range(0, n+1)):
            r = bn128_Field(1)
            nroots = 1 << i
            rootsi = {}

            for j in range(nroots):
                rootsi.update({j:r})
                r = r * self.w[i]

            self.roots.update({i : rootsi})

    def extend(self, p, e):
        if e == len(p):
            return p
        z = [field.zero()] * (e - len(p))
        return p + z

    def ifft(self, p):
        if len(p) <= 1:
            return p
        bits = log2(len(p) - 1) + 1
        self._set_roots(bits)
        m = 1 << bits
        ep = self.extend(p, m)
        res = self._fft(ep, bits, 0, 1)
        twoinvm = mul_scalar(self.field(0).one(), m).inv()
        resn = [None] * m
        for i in range(m):
            resn[i] = res[(m-i)%m] * twoinvm
        return resn

    def fft(self, p):
        if len(p) <= 1:
            return p
        bits = log2(len(p) - 1) + 1
        self._set_roots(bits)

        m = 1 << bits
        ep = self.extend(p, m)
        res = self._fft(ep, bits, 0, 1)
        return res

    def _fft(self, pall, bits, offset, step):
        n = 1 << bits
        if n == 1:
            return [pall[offset]]
        elif n == 2:
            return [
                pall[offset] + pall[offset + step],
                pall[offset] - pall[offset + step]
            ]

        ndiv2 = n >> 1
        p1 = self._fft(pall, bits-1, offset, step*2)
        p2 = self._fft(pall, bits-1, offset+step, step*2)
        out = [None] * n

        for i in range(ndiv2):
            out[i] = self.field(p1[i]) + self.roots[bits][i] * p2[i]
            out[i+ndiv2] = self.field(p1[i]) - self.roots[bits][i] * p2[i]

        return out

    def compute_vanishing_polynomial(self, bits: int, t: FQ):
        # t : toxic waste(셋업 마치면 사라져야되는 값)
        # m : constraints 수에 근접(A, B, C 행렬의 row 갯수), 무조껀 짝수
        # -> taget polynomial H * T = A*u + B*u - C*u
        m = 1 << bits
        return t**m - bn128_Field(1)

    def evaluate_lagrange_polynomials(self, bits: int, t: FQ) -> "Dict":
        m = 1 << bits
        tm = t ** m

        # print("m : "  , m )
        # print("t : "  , t )
        # print("t^m : ", tm)

        u = dict()
        for i in range(m):
            u.update( {i : 0} )
        self._set_roots(bits)
        omega = self.w[bits]

        #TODO : if tm == 1

        z = tm - bn128_Field(1)
        # print("z : ", z)
        l = z / bn128_Field(m)
        # print("l : ", l)

        for i in range(m):
            u[i] = l / (t - self.roots[bits][i])
            l = l * omega

        return u

