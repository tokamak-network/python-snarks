from wasmer import engine, Store, Module, Instance, Memory, MemoryType, ImportObject, Function, Value
from wasmer_compiler_cranelift import Compiler
import fnv
from itertools import chain
from ..arithmetic import FQ

def fn_error(code: int, pstr: int, a: int, b: int, c: int, d: int):
    #print(f"pywasm fn_error - ", code, pstr, a, b, c, d)
    raise Exception(code, pstr, a, b, c, d)
def fn_log(a: int):
    #print(f'fn_log: {a}')
    pass
def fn_logGetSignal(signal: int, pVal: int):
    #print(f'fn_logGetSignal: {signal}, {pVal}')
    pass
def fn_logSetSignal(signal: int, pVal: int):
    #print(f'logSetSignal: {signal}, {pVal}')
    pass
def fn_logStartComponent(cIdx: int):
    #print(f'logStartComponent: {cIdx}')
    pass
def fn_logFinishComponent(cIdx: int):
    #print(f'logFinishComponent: {cIdx}')
    pass

def p2str(p):
    i8 = bytearray(memory.buffer)
    buf = []
    i = 0
    while i8[p+i] > 0:
        buf.append(i8[p+i])
        i += 1
    return ''.join(map(unichr, buf))
    
class Field1(FQ):
    def __init__(self, val, field_modulus):
        self.field_modulus = field_modulus
        super().__init__(val, field_modulus)

    def new(self, val):
        return FQ(val, self.field_modulus)

    def one(self):
        return type(self)(1, self.field_modulus)

    def zero(self):
        return type(self)(0, self.field_modulus)

class Calculator:
    def __init__(self, wasm_path):
        store = Store(engine.JIT(Compiler))
        module = Module(store, open(wasm_path, 'rb').read())
        runtime = {
            'error': Function(store, fn_error),
            'log': Function(store, fn_log),
            'logGetSignal': Function(store, fn_logGetSignal),
            'logSetSignal': Function(store, fn_logSetSignal),
            'logStartComponent': Function(store, fn_logStartComponent),
            'logFinishComponent': Function(store, fn_logFinishComponent)
        }
        self.memory = Memory(store, MemoryType(2000, shared=False))
        import_object = ImportObject()
        import_object.register('env', {'memory': self.memory})
        import_object.register('runtime', runtime)
        self.instance = Instance(module, import_object)

        self.i32 = self.memory.int32_view()
        self.n32 = (self.instance.exports.getFrLen() >> 2) - 2
        pRawPrime = self.instance.exports.getPRawPrime()

        arr = [None] * self.n32
        for i in range(self.n32):
            arr[self.n32-1-i] = self.get_mem_uint32((pRawPrime >> 2) + i)

        acc = 0
        for i in range(len(arr)):
            acc = acc*0x100000000 + arr[i]
        self.prime = acc
        self.fr = Field1(0, self.prime)
        self.mask32 = 0xFFFFFFFF
        self.nvars = self.instance.exports.getNVars()
        self.n64 = (self.fr.bitLength - 1) // 64 + 1

        self.r = self.fr.new(1 << (self.n64*64))
        self.rinv = self.r.inv()

    def fr(self):
        return 

    def get_mem_uint32(self, pos):
        buf = self.i32[pos]
        return buf & 0xffffffff

    def set_mem_uint32(self, pos, value: int):
        self.i32[pos] = int(value)

    def alloc_int(self):
        p = self.get_mem_uint32(0)
        self.set_mem_uint32(0, p + 8)
        return p

    def alloc_fr(self):
        p = self.get_mem_uint32(0)
        self.set_mem_uint32(0, p + self.n32*4 + 8)
        return p

    def fnv_hash(self, data):
        return fnv.hash(data, algorithm=fnv.fnv_1a, bits=64)

    def get_fr(self, p):
        idx = p>>2
        if self.get_mem_uint32(idx + 1) & 0x80000000:
            arr = [None] * self.n32
            for i in range(self.n32):
                arr[self.n32-1-i] = self.get_mem_uint32(idx+2+i)

            acc = 0
            for i in range(len(arr)):
                acc = acc*0x100000000 + arr[i]
            res = self.fr.new(acc)
            if self.get_mem_uint32(idx + 1) & 0x40000000:
                return self.from_montgomery(res)
            else:
                return res
        else:
            if self.get_mem_uint32(idx) & 0x80000000:
                return self.fr.new(self.get_mem_uint32(idx) - 0x100000000)
            else:
                return self.fr.new(self.get_mem_uint32(idx))

    def from_montgomery(self, n):
        return self.rinv * n

    def set_fr(self, p, v):
        v = self.fr.new(v)
        min_short = self.fr.new(0x80000000).neg()
        max_short = self.fr.new(0x7FFFFFFF)
        if v >= min_short and v <= max_short:
            a = None
            if v >= self.fr.zero():
            #if v >= 0:
                a = v
            else:
                a = v - min_short
                a = a - 0x80000000
                a = 0x100000000 + a
            self.set_mem_uint32(p >> 2, a)
            self.set_mem_uint32((p >> 2) + 1, 0)
            return
        
        self.set_mem_uint32(p >> 2, 0)
        self.set_mem_uint32((p >> 2) + 1, 0x80000000)
        arr = self.to_array(v, 0x100000000)
        for i in range(self.n32):
            idx = len(arr) - 1 - i
            if idx >= 0:
                self.set_mem_uint32((p >> 2) + 2 + i, arr[idx])
            else:
                self.set_mem_uint32((p >> 2) + 2 + i, 0)

    def to_array(self, s, radix):
        res = []
        rem = s
        while rem:
            res.insert(0, rem % radix)
            rem = rem / radix
        return res

    def get_int(self, p):
        return self.get_mem_uint32(p>>2)

    def _doCalculateWitness(self, inputs):
        self.instance.exports.init(1)
        psig_offset = self.alloc_int()
        pfr = self.alloc_fr()
        for i, k in inputs.items():
            h = self.fnv_hash(list(map(ord, i)))
            h_msb = int(hex(h)[2:10], 16)
            h_lsb = int(hex(h)[10:], 16)
            h_msb -= (h_msb & 0x80000000) << 1
            h_lsb -= (h_lsb & 0x80000000) << 1
            tmp = self.get_mem_uint32(psig_offset)
            self.instance.exports.getSignalOffset32(psig_offset, 0, h_msb, h_lsb)
            tmp = self.get_mem_uint32(psig_offset)
            sig_offset = self.get_int(psig_offset)
            farr = [k]
            for j in range(len(farr)):
                self.set_fr(pfr, farr[j])
                self.instance.exports.setSignal(0, 0, sig_offset + j, pfr)

    def calculate(self, inputs):
        old0 = self.get_mem_uint32(0)
        w = []
        self._doCalculateWitness(inputs)
        for i in range(self.nvars):
            pwitness = self.instance.exports.getPWitness(i)
            w.append(self.get_fr(pwitness))
        self.set_mem_uint32(0, old0)
        return w
