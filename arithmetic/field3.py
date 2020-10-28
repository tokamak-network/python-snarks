from .field_elements import FQ
from .utils import mul_scalar, exp

class Field3:
    field_modulus = None
    non_residue = None
    val1 = None
    val2 = None
    def __init__(self, val1, val2, val3):
        if self.field_modulus is None:
            raise AttributeError("Field Modulus hasn't been specified")
        self.val1 = val1
        self.val2 = val2
        self.val3 = val3

    def __add__(self, other):
        return type(self)(self.val1 + other.val1, self.val2 + other.val2, self.val3 + other.val3)

    def __sub__(self, other):
        return type(self)(self.val1 - other.val1, self.val2 - other.val2, self.val3 - other.val3)

    def __mul__(self, other):
        a = self.val1 * other.val1
        b = self.val2 * other.val2
        c = self.val3 * other.val3
        return type(self)(
            a + self.mul_by_non_residue((self.val2 + self.val3) * (other.val2 + other.val3) - (b + c)),
            (self.val1 + self.val2) * (other.val1 + other.val2) - (a + b) + self.mul_by_non_residue(c),
            (self.val1 + self.val3) * (other.val1 + other.val3) - (a + c) + b
        )

    def __div__(self, other):
        return self * other.inv()

    def __eq__(self, other):
        return self.val1 == other.val1 and self.val2 == other.val2 and self.val3 == other.val3

    def __getitem__(self, idx):
        if idx == 0:
            return self.val1
        elif idx == 1:
            return self.val2
        elif idx == 2:
            return self.val3
        else:
            raise ValueError("Field index error")

    def __repr__(self):
        return repr("[" + str(self.val1) + ", " + str(self.val2) + ", " + str(self.val3) + "]")

    def mul_by_non_residue(self, v):
        return self.non_residue * v

    def double(self):
        return self + self

    def neg(self):
        self.zero - self

    def inv(self):
        t0 = self.val1.square()
        t1 = self.val2.square()
        t2 = self.val3.square()
        t3 = self.val1 * self.val2
        t4 = self.val1 * self.val3
        t5 = self.val2 * self.val3
        c0 = t0 - self.mul_by_non_residue(t5)
        c1 = self.mul_by_non_residue(t2) - t3
        c2 = t1 - t4
        t6 = ((self.val1 * c0) + self.mul_by_non_residue((self.val3 * c1) + (self.val2 * c2))).inv()
        return [
            t6 * c0,
            t6 * c1,
            t6 * c2
        ]

    def square(self):
        s0 = self.val1.square()
        ab = self.val1 * self.val2
        s1 = ab + ab
        s2 = (self.val1 - self.val2 + self.val3).square()
        bc = self.val2 * self.val3
        s3 = bc + bc
        s4 = self.val3.square()
        return [
            s0 + self.mul_by_non_residue(s3),
            s1 + self.mul_by_non_residue(s4),
            s1 + s2 + s3 - (s0 + s4)
        ]

    @classmethod
    def zero(cls):
        return None

    @classmethod
    def one(cls):
        return None

    def is_zero(self):
        return self.val1.is_zero() and self.val2.is_zero() and self.val3.is_zero()

    def mul_scalar(self, e):
        return mul_scalar(self, e)

    def exp(self, e):
        return exp(self, e)