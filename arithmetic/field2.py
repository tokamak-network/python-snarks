from .field_elements import FQ
from .utils import mul_scalar, exp

class Field2:
    field_modulus = None
    non_residue = None
    val1 = None
    val2 = None

    def __init__(self, *args):
        if len(args) == 1:
            self.val1 = args[0].val1
            self.val2 = args[0].val2
        elif len(args) == 2:
            self.val1 = args[0]
            self.val2 = args[1]

    def __add__(self, other):
        return type(self)(self.val1 + other.val1, self.val2 + other.val2)

    def __sub__(self, other):
        return type(self)(self.val1 - other.val1, self.val2 - other.val2)

    def __mul__(self, other):
        a = self.val1 * other.val1
        b = self.val2 * other.val2
        return type(self)(
            a + self.mul_by_non_residue(b),
            (self.val1 + self.val2) * (other.val1 + other.val2) - (a + b)
        )

    def __div__(self, other):
        return self * other.inv()

    def __eq__(self, other):
        return self.val1 == other.val1 and self.val2 == other.val2
    
    def __getitem__(self, idx):
        if idx == 0:
            return self.val1
        elif idx == 1:
            return self.val2
        else:
            raise ValueError("Field index error", idx)

    def mul_by_non_residue(self, v):
        return self.non_residue * v

    def double(self):
        return self + self

    def __neg__(self):
        return self.zero() - self

    def __repr__(self):
        return repr("[" + str(self.val1) + ", " + str(self.val2) + "]")

    def inv(self):
        t0 = self.val1.square()
        t1 = self.val2.square()
        t2 = t0 - self.mul_by_non_residue(t1)
        t3 = t2.inv()
        return type(self)(self.val1 * t3, -(self.val2 * t3))

    def square(self):
        a = self.val1 * self.val2
        b = (self.val1 + self.val2) * (self.val1 + self.mul_by_non_residue(self.val2)) 
        c = (a + self.mul_by_non_residue(a))
        d = a + a
        return type(self)(b - c, d)

    @classmethod
    def zero(cls):
        return None

    @classmethod
    def one(cls):
        return None

    def is_zero(self):
        return self.val1.is_zero() and self.val2.is_zero()

    def mul_scalar(self, e):
        return mul_scalar(self, e)

    def exp(self, e):
        return exp(self, e)