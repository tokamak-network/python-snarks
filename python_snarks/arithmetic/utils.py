from typing import (
    cast,
    Tuple,
    Sequence,
    Union,
    TYPE_CHECKING,
)
import os

def log2(val: int) -> "Int":
    if val & 0xFFFF0000 != 0:
        a = 16
        val &= 0xFFFF0000
    else:
        a = 0

    if val & 0xFF00FF00 != 0:
        b = 8
        val &= 0xFF00FF00
    else:
        b = 0

    if val & 0xF0F0F0F0 != 0:
        c = 4
        val &= 0xF0F0F0F0
    else:
        c = 0

    if val & 0xCCCCCCCC != 0:
        d = 2
        val &= 0xCCCCCCCC
    else:
        d = 0

    if val & 0xAAAAAAAA != 0:
        e = 1
    else:
        e = 0

    return a | b | c | d | e

def prime_field_inv(a: int, n: int) -> int:
    """
    Extended euclidean algorithm to find modular inverses for integers
    """
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n

# Utility methods for polynomial math
def deg(p: Sequence[Union[int, "FQ"]]) -> int:
    d = len(p) - 1
    while p[d] == 0 and d:
        d -= 1
    return d

def naf(n):
    res = []
    nn = int(n)
    while nn:
        if nn & 1:
            z = 2 - (nn % 4)
            res.append(z)
            nn = nn - z
        else:
            res.append(0)
        nn = nn >> 1
    return res

def mul_scalar(base, e):
    res = None
    if e == 0:
        return base.zero()
    n = naf(e)
    if n[len(n) - 1] == 1:
        res = base
    elif n[len(n) - 1] == -1:
        res = -base
    else:
        raise ValueError("mul_scalar error")

    for i in range(len(n) - 2, -1, -1):
        res = res + res
        if n[i] == 1:
            res = res + base
        elif n[i] == -1:
            res = res - base

    return res

def bits(n):
    return [int(x) for x in bin(n)[2:]]

def exp(base, e):
    if type(e) is int:
        if e == 0:
            return base.one()
    elif e.is_zero():
        return base.one()
    n = bits(e)
    if len(n) == 0:
        return base.one()
    res = base
    for i in range(1, len(n)):
        res = res.square()
        if n[i]:
            res = res * base
    return res

def random():
    return int.from_bytes(os.urandom(32), "little")
