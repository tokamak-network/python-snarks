from .utils import mul_scalar
from .curve_point import CurvePoint

class Curve:
    g = None
    field = None

    def __init__(self):
        pass

    def add(self, p1, p2):
        if self.eq(p1, self.zero()):
            return p2
        if self.eq(p2, self.zero()):
            return p1
        z1z1 = p1[2].square()
        z2z2 = p2[2].square()
        u1 = p1[0] * z2z2
        u2 = p2[0] * z1z1
        z1_cubed = p1[2] * z1z1
        z2_cubed = p2[2] * z2z2
        s1 = p1[1] * z2_cubed
        s2 = p2[1] * z1_cubed
        if u1 == u2 and s1 == s2:
            return self.double(p1)
        
        h = u2 - u1
        s_diff = s2 - s1
        i = (h + h).square()
        j = h * i
        r = s_diff + s_diff
        v = u1 * i

        res = [None]*3
        res[0] = (r.square() - j) - (v + v)
        s1_j = s1 * j
        res[1] = (r * (v - res[0])) - (s1_j + s1_j)
        res[2] = h * ((p1[2] + p2[2]).square() - (z1z1 + z2z2))
        return res

    def mul(p1, p2):
        pass

    def sub(self, p1, p2):
        #return p1 + self.neg(p2)
        return self.add(p1, self.neg(p2))

    def neg(self, p):
        return CurvePoint(self, [p[0], -p[1], p[2]])

    @classmethod
    def zero(cls):
        pass

    def double(self, p):
        if p == self.zero():
            return p

        a = p[0].square()
        b = p[1].square()
        c = b.square()
        d = (p[0] + b).square() - (a + c)
        d = d + d
        e = a + a + a
        f = e.square()

        res = [None] * 3
        
        res[0] = f - (d + d)
        eightC = c + c
        eightC = eightC + eightC
        eightC = eightC + eightC

        res[1] = (e * (d - res[0])) - eightC
        
        y1z1 = p[1] * p[2]
        res[2] = y1z1 + y1z1

        return CurvePoint(self, res)

    def mul_scalar(self, base, e):
        return mul_scalar(base, e)

    def affine(self, p):
        if self.eq(p, self.zero()):
            return self.zero()
        else:
            z_inv = p[2].inv()
            z2_inv = z_inv.square()
            z3_inv = z2_inv * z_inv

            res = [None] * 3
            res[0] = p[0] * z2_inv
            res[1] = p[1] * z3_inv
            res[2] = p[0].one()
            return CurvePoint(self, res)

    def multi_affine(self, arr):
        acc_mul = [None] * (len(arr) + 1)
        acc_mul[0] = self.field.one()
        for i in range(len(arr)):
            if arr[i] == None or arr[i][2] == self.field.zero():
                acc_mul[i+1] = acc_mul[i]
            else:
                acc_mul[i+1] = acc_mul[i] * arr[i][2]

        acc_mul[len(arr)] = acc_mul[len(arr)].inv()

        for i in range(len(arr) - 1, -1, -1):
            if arr[i] == None or arr[i][2] == self.field.zero():
                acc_mul[i] = acc_mul[i+1]
                arr[i] = self.zero()
            else:
                z_inv = acc_mul[i] * acc_mul[i+1]
                acc_mul[i] = arr[i][2] * acc_mul[i+1]

                z2_inv = z_inv.square()
                z3_inv = z2_inv * z_inv

                arr[i][0] = arr[i][0] * z2_inv
                arr[i][1] = arr[i][1] * z3_inv
                arr[i][2] = self.field.one()
        return arr
    def eq(self, p1, p2):
        if p1[2] == p1[2].zero():
            return p2[2] == p2[2].zero()
        if p2[2] == p2[2].zero():
            return False

        z1z1 = p1[2].square()
        z2z2 = p2[2].square()

        u1 = p1[0] * z2z2
        u2 = p2[0] * z1z1

        z1_cubed = p1[2] * z1z1
        z2_cubed = p2[2] * z2z2

        s1 = p1[1] * z2_cubed
        s2 = p2[1] * z1_cubed

        return u1 == u2 and s1 == s2
