import os
import json

from ..arithmetic import bn128_Field, bn128_FieldPolynomial, log2, mul_scalar, G1, G2, pairing, FQ, field_properties
from ..r1csfile import R1cs

class Groth:
    def __init__(self, r1cs_path):
        self.r1cs = R1cs(r1cs_path)

        num_vars = int(self.r1cs.nVars)

        self.setup = {
            "vk_proof" : {
                "protocol" : "groth",
                "nVars"    : int(self.r1cs.nVars),
                "nPublic"  : int(self.r1cs.nPubInputs + self.r1cs.nOutputs),
                "domainBits" : 0,
                "domainSize" : 0,
                "polsA" : [dict() for x in range(num_vars)],
                "polsB" : [dict() for x in range(num_vars)],
                "polsC" : [dict() for x in range(num_vars)]
            },
            "vk_verifier": {
                "protocol" : "groth",
                "nPublic"  : int(self.r1cs.nPubInputs + self.r1cs.nOutputs)
            },
            "toxic" : {
                "t" : None,
                "kalpha" : None,
                "kbeta" : None,
                "kgamma" : None,
                "kdelta" : None
            },
            "qap" : {
                "a_t" : None,
                "b_t" : None,
                "c_t" : None,
                "z_t" : None
            }

        }
        total_domain = int(self.r1cs.nConstraints) + int(self.r1cs.nPubInputs) + int(self.r1cs.nOutputs)
        self.setup["vk_proof"]["domainBits"] = log2(total_domain) + 1
        self.setup["vk_proof"]["domainSize"] = 1 << self.setup["vk_proof"]["domainBits"]

        #self.setup["toxic"]["t"] = FQ(5, field_properties["bn128"]["r"])
        # self.setup["toxic"]["t"] = FQ(0, field_properties["bn128"]["r"]).random()

        self.PF = bn128_FieldPolynomial()

    def setup_zk(self, toxic=None):
        if self.setup["toxic"]["t"] != None:
            pass
        else:
            self.update_toxic(toxic)

        self.calc_polynomials()
        self.calc_values_at_T()
        self.calc_encrypted_values_at_T()

    # toxic = {"t" : value, "kalpha" : value, "kbeta" : value, "kgamma" : value, "kdelta" : value}
    def update_toxic(self, toxic=None):
        if toxic == None:
            self.setup["toxic"].update({
                "t" : FQ(0, field_properties["bn128"]["r"]).random(),
                "kalpha" : FQ(0, field_properties["bn128"]["r"]).random(),
                "kbeta" : FQ(0, field_properties["bn128"]["r"]).random(),
                "kgamma" : FQ(0, field_properties["bn128"]["r"]).random(),
                "kdelta" : FQ(0, field_properties["bn128"]["r"]).random()
            })
        else:
            self.setup["toxic"].update({
                "t" : toxic["t"],
                "kalpha" : toxic["kalpha"],
                "kbeta" : toxic["kbeta"],
                "kgamma" : toxic["kgamma"],
                "kdelta" : toxic["kdelta"]
            })

        return self.setup["toxic"]

    def calc_polynomials(self):
        num_constraints = len(self.r1cs.constraints)
        for c in range(num_constraints):
            A = self.r1cs.constraints[c][0]
            B = self.r1cs.constraints[c][1]
            C = self.r1cs.constraints[c][2]
            for s in A:
                if s in A:
                    self.setup["vk_proof"]["polsA"][int(s)][c] = FQ(int(A[s]), field_properties["bn128"]["r"])
            for s in B:
                if s in B:
                    self.setup["vk_proof"]["polsB"][int(s)][c] = FQ(int(B[s]), field_properties["bn128"]["r"])
            for s in C:
                if s in C:
                    self.setup["vk_proof"]["polsC"][int(s)][c] = FQ(int(C[s]), field_properties["bn128"]["r"])

        n_pub_plus_n_out = int(self.r1cs.nPubInputs) + int(self.r1cs.nOutputs)
        for i in range(n_pub_plus_n_out+1):
            self.setup["vk_proof"]["polsA"][i][num_constraints+i] = FQ(1, field_properties["bn128"]["r"]) # bn128_Field

    def calc_values_at_T(self):
        domain_bits = self.setup["vk_proof"]["domainBits"]
        toxic_t = self.setup["toxic"]["t"]
        z_t = self.PF.compute_vanishing_polynomial(domain_bits, toxic_t)
        u = self.PF.evaluate_lagrange_polynomials(domain_bits, toxic_t)

        n_vars = int(self.r1cs.nVars)

        a_t = [FQ(0, field_properties["bn128"]["r"])]*n_vars
        b_t = [FQ(0, field_properties["bn128"]["r"])]*n_vars
        c_t = [FQ(0, field_properties["bn128"]["r"])]*n_vars

        for s in range(n_vars):
            A = self.setup["vk_proof"]["polsA"][s]
            B = self.setup["vk_proof"]["polsB"][s]
            C = self.setup["vk_proof"]["polsC"][s]
            if A != None:
                for c in A:
                    a_t[s] = a_t[s] + u[int(c)] * int(A[c])

            if B != None:
                for c in B:
                    b_t[s] = b_t[s] + u[int(c)] * int(B[c])

            if C != None:
                for c in C:
                    c_t[s] = c_t[s] + u[int(c)] * int(C[c])

        self.setup["qap"].update({
            "a_t" : a_t,
            "b_t" : b_t,
            "c_t" : c_t,
            "z_t" : z_t
        })

        return self.setup["qap"]


    def calc_encrypted_values_at_T(self):
        num_vars = int(self.r1cs.nVars)
        n_pub_plus_n_out = int(self.r1cs.nPubInputs) + int(self.r1cs.nOutputs) + 1

        # a_t, b_t, c_t, z_t = self.calc_values_at_T()
        a_t = self.setup["qap"]["a_t"]
        b_t = self.setup["qap"]["b_t"]
        c_t = self.setup["qap"]["c_t"]
        z_t = self.setup["qap"]["z_t"]

        vk_proof_A = [None]*num_vars
        vk_proof_B1 = [None]*num_vars
        vk_proof_B2 = [None]*num_vars
        vk_proof_C = [None]*num_vars
        vk_proof_IC = [None]*n_pub_plus_n_out

        kalpha = self.setup["toxic"]["kalpha"]
        kbeta = self.setup["toxic"]["kbeta"]
        kgamma = self.setup["toxic"]["kgamma"]
        kdelta = self.setup["toxic"]["kdelta"]

        inv_delta = 1 / kdelta
        inv_gamma = 1 / kgamma

        g1 = G1()
        g2 = G2()

        vk_proof_alpha_1 = mul_scalar(g1.g, kalpha).affine()
        vk_proof_beta_1 = mul_scalar(g1.g, kbeta).affine()
        vk_proof_delta_1 = mul_scalar(g1.g, kdelta).affine()

        vk_proof_beta_2 = mul_scalar(g2.g, kbeta).affine()
        vk_proof_delta_2 = mul_scalar(g2.g, kdelta).affine()

        vk_verifier_alpha_1 = vk_proof_alpha_1

        vk_verifier_beta_2 = vk_proof_beta_2
        vk_verifier_gamma_2 = mul_scalar(g2.g, kgamma).affine()
        vk_verifier_delta_2 = vk_proof_delta_2

        vk_verifier_alphabeta_12 = pairing(vk_verifier_alpha_1, vk_verifier_beta_2)

        for i in range(num_vars):
            A = mul_scalar(g1.g, a_t[i])
            vk_proof_A[i] = A
            B1 = mul_scalar(g1.g, b_t[i])
            vk_proof_B1[i] = B1
            B2 = mul_scalar(g2.g, b_t[i])
            vk_proof_B2[i] = B2

        for i in range(self.setup["vk_proof"]["nPublic"] + 1):
            ps = ((a_t[i] * kbeta) + (b_t[i] * kalpha) + c_t[i]) * inv_gamma
            IC = mul_scalar(g1.g, ps)
            vk_proof_IC[i] = IC

        for i in range(self.setup["vk_proof"]["nPublic"] + 1, num_vars):
            ps = ((a_t[i] * kbeta) + (b_t[i] * kalpha) + c_t[i]) * inv_delta
            C = mul_scalar(g1.g, ps)
            vk_proof_C[i] = C

        maxH = self.setup["vk_proof"]["domainSize"] + 1

        hExps = [None] * maxH
        zod = inv_delta * z_t
        hExps[0] = mul_scalar(g1.g, zod)

        eT = toxic_t = self.setup["toxic"]["t"]

        for i in range(1, maxH):
            hExps[i] = mul_scalar(g1.g, eT * zod)
            eT = eT * toxic_t

        self.setup["vk_proof"]["hExps"] = hExps

        self.setup["vk_proof"].update({
            "hExps": hExps,
            "A": vk_proof_A,
            "B1": vk_proof_B1,
            "B2": vk_proof_B2,
            "C": vk_proof_C,
            "vk_alpha_1": vk_proof_alpha_1,
            "vk_beta_1": vk_proof_beta_1,
            "vk_delta_1": vk_proof_delta_1,
            "vk_beta_2": vk_proof_beta_2,
            "vk_delta_2": vk_proof_delta_2
        })

        self.setup["vk_verifier"].update({
            "IC": vk_proof_IC,
            "vk_alphabeta_12": vk_verifier_alphabeta_12,
            "vk_alpha_1": vk_verifier_alpha_1,
            "vk_beta_2": vk_verifier_beta_2,
            "vk_gamma_2": vk_verifier_gamma_2,
            "vk_delta_2": vk_verifier_delta_2
        })

        self.setup["toxic"].update({
            "t": toxic_t,
            "kalpha": kalpha,
            "kbeta": kbeta,
            "kgamma": kgamma,
            "kdelta": kdelta
        })

        A = self.setup["vk_proof"]["A"]
        B1 = self.setup["vk_proof"]["B1"]
        B2 = self.setup["vk_proof"]["B2"]
        C = self.setup["vk_proof"]["C"]
        hExps = self.setup["vk_proof"]["hExps"]
        IC = self.setup["vk_verifier"]["IC"]

        self.setup["vk_proof"]["A"] = g1.multi_affine(A)
        self.setup["vk_proof"]["B1"] = g1.multi_affine(B1)
        self.setup["vk_proof"]["B2"] = g2.multi_affine(B2)
        self.setup["vk_proof"]["C"] = g1.multi_affine(C)
        self.setup["vk_proof"]["hExps"] = g1.multi_affine(hExps)
        self.setup["vk_verifier"]["IC"] = g1.multi_affine(IC)

    def export_solidity_verifier(self, output_path):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_path = dir_path + "/template/groth16_verifier.sol"

        with open(template_path, "r") as f:
            data = f.read()

            vkalpha1_str = str(self.setup["vk_verifier"]["vk_alpha_1"][0]) + "," + str(self.setup["vk_verifier"]["vk_alpha_1"][1])
            data = data.replace("<%vk_alpha1%>", vkalpha1_str)


            vkbeta2_str = "[" + str(self.setup["vk_verifier"]["vk_beta_2"][0][1]) + ", " + \
                str(self.setup["vk_verifier"]["vk_beta_2"][0][0]) + "], [" + \
                str(self.setup["vk_verifier"]["vk_beta_2"][1][1]) + ", " + \
                str(self.setup["vk_verifier"]["vk_beta_2"][1][0]) + "]"
            data = data.replace("<%vk_beta2%>", vkbeta2_str)

            vkgamma2_str = "[" + str(self.setup["vk_verifier"]["vk_gamma_2"][0][1]) + ", " + \
                str(self.setup["vk_verifier"]["vk_gamma_2"][0][0]) + "], [" + \
                str(self.setup["vk_verifier"]["vk_gamma_2"][1][1]) + ", " + \
                str(self.setup["vk_verifier"]["vk_gamma_2"][1][0]) + "]"
            data = data.replace("<%vk_gamma2%>", vkgamma2_str)

            vkdelta2_str = "[" + str(self.setup["vk_verifier"]["vk_delta_2"][0][1]) + ", " +  \
                str(self.setup["vk_verifier"]["vk_delta_2"][0][0]) + "], [" +  \
                str(self.setup["vk_verifier"]["vk_delta_2"][1][1]) + ", " +  \
                str(self.setup["vk_verifier"]["vk_delta_2"][1][0]) + "]"
            data = data.replace("<%vk_delta2%>", vkdelta2_str)

            data = data.replace("<%vk_input_length%>", str(len(self.setup["vk_verifier"]["IC"]) - 1))
            data = data.replace("<%vk_ic_length%>", str(len(self.setup["vk_verifier"]["IC"])))

            vi = ""
            for i in range(len(self.setup["vk_verifier"]["IC"])):
                if vi != "":
                    vi = vi + "        "
                vi = vi + f'vk.IC[{i}] = Pairing.G1Point({str(self.setup["vk_verifier"]["IC"][i][0])},' + \
                    f'{str(self.setup["vk_verifier"]["IC"][i][1])});\n'
            data = data.replace("<%vk_ic_pts%>", vi)

            with open(output_path, "w") as output:
                output.write(data)

if __name__ == "__main__":
    ## setup
    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.r1cs")
    gr.setup_zk()
