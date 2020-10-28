from .field_properties import field_properties
from .field_elements import FQ
from .field2 import Field2
from .field3 import Field3
from functools import partial

bn128_Field = partial(FQ, field_modulus = field_properties["bn128"]["r"])

class bn128_Field2(Field2):
    field_modulus = field_properties["bn128"]["q"]
    non_residue = 21888242871839275222246405745257275088696311157297823662689037894645226208582
