

class CurvePoint:
    def __init__(self, c, p):
        self.curve = c
        self.p = p

    def __add__(self, other):
        return CurvePoint(self.curve, self.curve.add(self.p, other.p))

    def __radd__(self, other):
        return CurvePoint(self.curve, self.curve.add(self.p, other.p))

    def __mul__(self, other):
        return CurvePoint(self.curve, self.curve.mul(self.p, other.p))

    def __rmul__(self, other):
        return CurvePoint(self.curve, self.curve.mul(self.p, other.p))

    def __sub__(self, other):
        return CurvePoint(self.curve, self.curve.sub(self.p, other.p))

    def __neg__(self):
        return CurvePoint(self.curve, self.curve.neg(self.p))

    def __getitem__(self, idx):
        return self.p[idx]

    def __setitem__(self, idx, v):
        self.p[idx] = v

    def __repr__(self):
        return repr(self.p)

    def double(self):
        return CurvePoint(self.curve, self.curve.double(self.p))

    def mul_scalar(self, e):
        return CurvePoint(self.curve, self.curve.mul_scalar(self.p, e))

    def affine(self):
        return CurvePoint(self.curve, self.curve.affine(self.p))

    def multi_affine(self, arr):
        pass

    def eq(self, other):
        return self.curve.eq(self.p, other.p)

    def zero(self):
        return self.curve.zero()

    def one(self):
        return self.p.one()
