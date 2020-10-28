from ..arithmetic import FQ

class R1cs:
    def __init__(self, path):
        self.load(path)

    def read_int32(self):
        return int.from_bytes(self.f.read(4), byteorder="little")

    def read_int64(self):
        return int.from_bytes(self.f.read(8), byteorder="little")

    def read_bigint(self, len):
        return int.from_bytes(self.f.read(len), byteorder="little")

    def load(self, path):
        self.f = open(path, "rb")
        b = self.f.read(4)
        if b.decode("utf-8") != "r1cs":
            raise Exception("Invalid file format: " + str(b))
        p = 4
        v = self.read_int32()
        if v > 1:
            raise Exception("Version not supported")
        n_sections = self.read_int32()
        header_pos = None
        constraints_pos = None
        header_size = None
        constraints_size = None
        map_pos = None
        map_size = None
        for i in range(n_sections):
            ht = self.read_int32()
            hl = self.read_int64()
            if ht == 1:
                if header_pos != None:
                    raise Exception("File has two headder sections")
                header_pos = self.f.tell()
                header_size = hl
            elif ht == 2:
                if constraints_pos != None:
                    raise Exception("File has two constraints sections")
                constraints_pos = self.f.tell()
                constraints_size = hl
            elif ht == 3:
                map_pos = self.f.tell()
                map_size = hl
            self.f.seek(hl, 1)
        
        if header_pos == None:
            raise Exception("File has no header")
        self.f.seek(header_pos)
        self.n8 = self.read_int32()
        self.prime = self.read_bigint(self.n8)
        self.nVars = self.read_int32()
        self.nOutputs = self.read_int32()
        self.nPubInputs = self.read_int32()
        self.nPrvInputs = self.read_int32()
        self.nLabels = self.read_int64()
        self.nConstraints = self.read_int32()

        if self.f.tell() != header_pos + header_size:
            raise Exception("Invalid header section size")

        self.f.seek(constraints_pos)
        self.constraints = []
        for i in range(self.nConstraints):
            c = self.read_constraint()
            self.constraints.append(c)
        if self.f.tell() != constraints_pos + constraints_size:
            raise Exception("Invalid constraints size")
        self.f.close()

    def read_constraint(self):
        c = []
        c.append(self.read_lc())
        c.append(self.read_lc())
        c.append(self.read_lc())
        return c

    def read_lc(self):
        lc = {}
        n_idx = self.read_int32()
        for i in range(n_idx):
            idx = self.read_int32()
            fr_value = self.read_bigint(self.n8)
            val = FQ(fr_value, self.prime)
            lc[idx] = val
        return lc