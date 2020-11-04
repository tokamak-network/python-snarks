from .field import bn128_Field, FQ, Field2, Field3, field_properties
from .curve import Curve
from .curve_point import CurvePoint
from .field_polynomial import FieldPolynomial
from .utils import mul_scalar
from functools import partial

class F1(FQ):
    field_modulus = field_properties["bn128"]["q"]
    def __init__(self, val, field_modulus=field_properties["bn128"]["q"]):
        super().__init__(val, field_properties["bn128"]["q"])

class F1_P(FQ):
    field_modulus = field_properties["bn128"]["r"]
    def __init__(self, val, field_modulus=field_properties["bn128"]["r"]):
        super().__init__(val, field_properties["bn128"]["r"])

class F2(Field2):
    field_modulus = field_properties["bn128"]["q"]
    non_residue = F1(field_properties["bn128"]["non_residue"])

    @classmethod
    def zero(cls):
        return cls(F1.zero(), F1.zero())
    @classmethod
    def one(cls):
        return cls(F1.one(), F1.zero())

non_residue_F6 = F2(F1(9), F1(1))
class F2_12(F2):
    non_residue = non_residue_F6
    def mul_by_non_residue(self, v):
        return type(self.val1)(self.non_residue * v[2], v[0], v[1])

class F3(Field3):
    field_modulus = field_properties["bn128"]["q"]
    non_residue = non_residue_F6
    @classmethod
    def zero(cls):
        return F3(F1.zero(), F1.zero(), F1.zero())
    @classmethod
    def one(cls):
        return F3(F1.one(), F1.zero(), F1.zero())
    
f2_zero = F2(F1(0), F1(0))
f2_one = F2(F1(1), F1(0))
f6_zero = F3(F2(F1(0), F1(0)), F2(F1(0), F1(0)), F2(F1(0), F1(0)))
f6_one = F3(F2(F1(1), F1(0)), F2(F1(0), F1(0)), F2(F1(0), F1(0)))
f12_one = F2_12(f6_one, f6_zero)

class F12(F2_12):
    non_residue = non_residue_F6
    def __init__(self, val1, val2, non_residue=non_residue_F6):
        self.val1 = F3(val1[0], val1[1], val1[2])
        self.val2 = F3(val2[0], val2[1], val2[2])

class PolField(FQ):
    field_modulus = field_properties["bn128"]["r"]
    def __init__(self, val, field_modulus=field_properties["bn128"]["r"]):
        super().__init__(val, self.field_modulus)
    def zero(self):
        return PolField(0)

class bn128_FieldPolynomial(FieldPolynomial):
    field = PolField

class G1(Curve):
    field = F1(0)
    def __init__(self):
        self.g = CurvePoint(self, [F1(1), F1(2), F1(1)])
    def zero(self):
        return CurvePoint(self, [F1(0), F1(1), F1(0)])

class G2(Curve):
    field = F2()
    def __init__(self):
        self.g = CurvePoint(self, [
            F2(F1(10857046999023057135944570762232829481370756359578518086990519993285655852781),
                F1(11559732032986387107991004021392285783925812861821192530917403151452391805634)),
            F2(F1(8495653923123431417604973247489272438418190587263600148770280649306958101930),
                F1(4082367875863433681332203403145435568316851327593401208105741076214120093531)),
            F2(F1(1), F1(0))
        ])
    def zero(self):
        return CurvePoint(self, [f2_zero, f2_one, f2_zero])

class G1Point(CurvePoint):
    curve = G1

class G2Point(CurvePoint):
    curve = G2

loop_count = None
loop_count_bits = None
two_inv = None
twist = None
twist_coeff_b = None
frobenius_coeffs_c1_1 = None
twist_mul_by_q_X = None
twist_mul_by_q_Y = None
final_exponent = None
def prepare_pairing():
    global loop_count
    global loop_count_bits
    global two_inv
    global twist
    global twist_coeff_b
    global frobenius_coeffs_c1_1
    global twist_mul_by_q_X
    global twist_mul_by_q_Y
    global final_exponent
    loop_count = 29793968203157093288
    if loop_count < 0:
        loop_count = -loop_count
    
    lc = loop_count
    loop_count_bits = [int(x) for x in bin(lc)[2:]]
    two_inv = F1(2).inv()
    coef_b = F1(3)
    twist = F2(F1(9), F1(1))
    twist_coeff_b = twist.inv().mul_scalar(coef_b)

    frobenius_coeffs_c1_1 = F1(field_properties["bn128"]["non_residue"])
    twist_mul_by_q_X = F2(
        F1(21575463638280843010398324269430826099269044274347216827212613867836435027261),
        F1(10307601595873709700152284273816112264069230130616436755625194854815875713954)
    )
    twist_mul_by_q_Y = F2(
        F1(2821565182194536844548159561693502659359617185244120367078079554186484126554),
        F1(3505843767911556378687030309984248845540243509899259641013678093033130930403)
    )
    final_exponent = 552484233613224096312617126783173147097382103762957654188882734314196910839907541213974502761540629817009608548654680343627701153829446747810907373256841551006201639677726139946029199968412598804882391702273019083653272047566316584365559776493027495458238373902875937659943504873220554161550525926302303331747463515644711876653177129578303191095900909191624817826566688241804408081892785725967931714097716709526092261278071952560171111444072049229123565057483750161460024353346284167282452756217662335528813519139808291170539072125381230815729071544861602750936964829313608137325426383735122175229541155376346436093930287402089517426973178917569713384748081827255472576937471496195752727188261435633271238710131736096299798168852925540549342330775279877006784354801422249722573783561685179618816480037695005515426162362431072245638324744480
prepare_pairing()

def double_step(current):
    x = current["X"]
    y = current["Y"]
    z = current["Z"]

    a = mul_scalar(x * y, two_inv)
    b = y.square()
    c = z.square()
    d = c + c + c
    e = twist_coeff_b * d
    f = e + e + e
    g = mul_scalar(b + f, two_inv)
    h = (y + z).square() - (b + c)
    i = e - b
    j = x.square()
    e_squared = e.square()

    current["X"] = a * (b - f)
    current["Y"] = (g.square() - e_squared) - (e_squared + e_squared)
    current["Z"] = b * h
    return {
        "ell_0": i * twist,
        "ell_VW": -h,
        "ell_VV": j + j + j
    }

def add_step(base, current):
    x1 = current["X"]
    y1 = current["Y"]
    z1 = current["Z"]
    x2 = base[0]
    y2 = base[1]

    d = x1 - (x2 * z1)
    e = y1 - (y2 * z1)
    f = d.square()
    g = e.square()
    h = d * f
    i = x1 * f
    j = h + (z1 * g) - (i + i)
    current["X"] = d * j
    current["Y"] = e * (i - j) - (h * y1)
    current["Z"] = z1 * h
    c = {
        "ell_0": twist * (e * x2 - d * y2),
        "ell_VV": -e,
        "ell_VW": d
    }
    return c

def g2_mul_by_q(p):
    fmx = F2(p[0][0], p[0][1] * frobenius_coeffs_c1_1)
    fmy = F2(p[1][0], p[1][1] * frobenius_coeffs_c1_1)
    fmz = F2(p[2][0], p[2][1] * frobenius_coeffs_c1_1)
    return type(p)(p.curve, F3(
        twist_mul_by_q_X * fmx,
        twist_mul_by_q_Y * fmy,
        fmz
    ))

def _mul_by_024(a, ell_0, ell_VW, ell_VV):
    z0 = a[0][0]
    z1 = a[0][1]
    z2 = a[0][2]
    z3 = a[1][0]
    z4 = a[1][1]
    z5 = a[1][2]

    x0 = ell_0
    x2 = ell_VV
    x4 = ell_VW

    d0 = z0 * x0
    d2 = z2 * x2
    d4 = z4 * x4
    t2 = z0 + z4
    t1 = z0 + z2
    s0 = z1 + z3 + z5

    s1 = z1 * x2
    t3 = s1 + d4
    t4 = non_residue_F6 * t3 + d0
    z0 = t4

    t3 = z5 * x4
    s1 = s1 + t3
    t3 = t3 + d2
    t4 = non_residue_F6 * t3
    t3 = z1 * x0
    s1 = s1 + t3
    t4 = t4 + t3
    z1 = t4

    t0 = x0 + x2
    t3 = (t1 * t0) - (d0 + d2)
    t4 = z3 * x4
    s1 = s1 + t4

    t0 = z2 + z4
    z2 = t3 + t4
    t1 = x2 + x4
    t3 = (t0 * t1) - (d2 + d4)

    t4 = non_residue_F6 * t3
    t3 = z3 * x0
    s1 = s1 + t3
    t4 = t4 + t3
    z3 = t4

    t3 = z5 * x2
    s1 = s1 + t3
    t4 = non_residue_F6 * t3
    t0 = x0 + x4
    t3 = (t2 * t0) - (d0 + d4)
    t4 = t4 + t3
    z4 = t4

    t0 = x0 + x2 + x4
    t3 = s0 * t0 - s1
    z5 = t3

    return F2_12(
        F3(F2(z0), F2(z1), F2(z2)),
        F3(F2(z3), F2(z4), F2(z5))
    )

def precomputeG1(p):
    p_copy = p.affine()
    res = {
        "PX": p_copy[0],
        "PY": p_copy[1]
    }
    return res

def precomputeG2(p):
    q_copy = p.affine()
    res = {
        "QX": q_copy[0],
        "QY": q_copy[1],
        "coeffs": []
    }
    R = {
        "X": q_copy[0],
        "Y": q_copy[1],
        "Z": f2_one
    }

    for i in range(1, len(loop_count_bits)):
        bit = loop_count_bits[i]
        c = double_step(R)
        res["coeffs"].append(c)
        if bit:
            c = add_step(q_copy, R)
            res["coeffs"].append(c)

    q1 = g2_mul_by_q(q_copy).affine()
    if q1[2] != f2_one:
        raise ValueError("value error")
    q2 = g2_mul_by_q(q1).affine()
    if q2[2] != f2_one:
        raise ValueError("value error")

    if loop_count < 0:
        R["Y"] = -R["Y"]
    q2[1] = -q2[1]
    c = add_step(q1, R)
    res["coeffs"].append(c)
    c = add_step(q2, R)
    res["coeffs"].append(c)
    return res

def miller_loop(pre1, pre2):
    f = f12_one
    idx = 0
    for i in range(1, len(loop_count_bits)):
        bit = loop_count_bits[i]
        c = pre2["coeffs"][idx]
        idx += 1
        f = f.square()
        f = _mul_by_024(
            f,
            c["ell_0"],
            mul_scalar(c["ell_VW"], pre1["PY"]),
            mul_scalar(c["ell_VV"], pre1["PX"])
        )
        if bit:
            c = pre2["coeffs"][idx]
            idx += 1
            f = _mul_by_024(
                f,
                c["ell_0"],
                mul_scalar(c["ell_VW"], pre1["PY"]),
                mul_scalar(c["ell_VV"], pre1["PX"])
            )

    if loop_count < 0:
        f = f.inv()
    c = pre2["coeffs"][idx]
    idx += 1
    f = _mul_by_024(
        f,
        c["ell_0"],
        mul_scalar(c["ell_VW"], pre1["PY"]),
        mul_scalar(c["ell_VV"], pre1["PX"])
    )
    c = pre2["coeffs"][idx]
    idx += 1
    f = _mul_by_024(
        f,
        c["ell_0"],
        mul_scalar(c["ell_VW"], pre1["PY"]),
        mul_scalar(c["ell_VV"], pre1["PX"])
    )
    return f

def final_exponentiation(elt):
    res = elt.exp(final_exponent)
    return res

def pairing(p1, p2):
    pre1 = precomputeG1(p1)
    pre2 = precomputeG2(p2)
    r1 = miller_loop(pre1, pre2)
    res = final_exponentiation(r1)
    return res