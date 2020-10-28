try:
    # Python 3.8
    from functools import cached_property  # type: ignore
except (ImportError, SyntaxError):
    # Python 3 to 3.7
    from cached_property import cached_property


from typing import (  # noqa: F401
    cast,
    List,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    TYPE_CHECKING,
)

from .utils import (
    deg,
    prime_field_inv,
    random
)

if TYPE_CHECKING:
    from py_ecc.typing import (  # noqa: F401
        FQ2_modulus_coeffs_type,
        FQ12_modulus_coeffs_type,
    )


# These new TypeVars are needed because these classes are kind of base classes and
# we need the output type to correspond to the type of the inherited class
T_FQ = TypeVar('T_FQ', bound="FQ")
IntOrFQ = Union[int, T_FQ]

class FQ(object):
    """
    A class for field elements in FQ. Wrap a number in this class,
    and it becomes a field element.
    """
    n = None  # type: int
    field_modulus = None  # type: int

    def __init__(self: T_FQ, val: IntOrFQ, field_modulus) -> None:
        self.field_modulus = field_modulus

        if isinstance(val, FQ):
            self.n = val.n
        elif isinstance(val, int):
            self.n = val % self.field_modulus
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(val))
            )
        self.bitLength = len(bin(self.field_modulus)) - 2
        self.half = self.field_modulus >> 1

    def __add__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((self.n + on) % self.field_modulus, self.field_modulus)

    def __mul__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((self.n * on) % self.field_modulus, self.field_modulus)

    def __rmul__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self * other

    def __radd__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self + other

    def __rsub__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((on - self.n) % self.field_modulus, self.field_modulus)

    def __sub__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((self.n - on) % self.field_modulus, self.field_modulus)

    def __mod__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        raise NotImplementedError("Modulo Operation not yet supported by fields")

    def __div__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)(
            self.n * prime_field_inv(on, self.field_modulus) % self.field_modulus,
            self.field_modulus
        )

    def __truediv__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self.__div__(other)

    def __rdiv__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)(
            prime_field_inv(self.n, self.field_modulus) * on % self.field_modulus,
            self.field_modulus
        )

    def __rtruediv__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self.__rdiv__(other)

    def __pow__(self: T_FQ, other: int) -> T_FQ:
        if other == 0:
            return type(self)(1, self.field_modulus)
        elif other == 1:
            return type(self)(self.n, self.field_modulus)
        elif other % 2 == 0:
            return (self * self) ** (other // 2)
        else:
            return ((self * self) ** int(other // 2)) * self

    def __eq__(self: T_FQ, other: IntOrFQ) -> bool:
        if isinstance(other, FQ):
            return self.n == other.n
        elif isinstance(other, int):
            return self.n == other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )
    
    def __ge__(self, other):
        aa = self.n - self.field_modulus if (self.n > self.half) else self.n
        bb = other.n - self.field_modulus if (other.n > self.half) else other.n
        return aa >= bb
    
    def __le__(self, other):
        aa = self.n - self.field_modulus if (self.n > self.half) else self.n
        bb = other.n - self.field_modulus if (other.n > self.half) else other.n
        return aa <= bb

    def __ne__(self: T_FQ, other: IntOrFQ) -> bool:
        return not self == other

    def __neg__(self: T_FQ) -> T_FQ:
        return type(self)(-self.n, self.field_modulus)

    def __repr__(self: T_FQ) -> str:
        return repr(self.n)

    def __int__(self: T_FQ) -> int:
        return self.n

    def neg(self):
        return -self

    @classmethod
    def one(cls) -> T_FQ:
        return cls(1, cls.field_modulus)

    @classmethod
    def zero(cls) -> T_FQ:
        return cls(0, cls.field_modulus)

    def square(self):
        return type(self)(self.n * self.n % self.field_modulus, self.field_modulus)

    def inv(self):
        t = 0
        r = self.field_modulus
        newt = 1
        newr = self.n
        while newr:
            q = r // newr
            [t, newt] = [newt, t - q*newt]
            [r, newr] = [newr, r - q*newr]
        if t < 0:
            t += self.field_modulus
        return type(self)(t, self.field_modulus)

    def random(self):
        self.n = random() % self.field_modulus
        return self
