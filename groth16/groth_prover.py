import os
import json

from ..arithmetic import bn128_Field, bn128_FieldPolynomial, log2, mul_scalar, G1, G2, pairing, CurvePoint, PolField, F1_P
from .groth_setup import Groth
from .witness_calculator import Calculator

def gen_proof(vk_proof, witness):
    g1 = G1()
    g2 = G2()
    pol = bn128_FieldPolynomial()

    #r = F1_P(5)
    #s = F1_P(5)
    r = F1_P(0).random()
    s = F1_P(0).random()

    proof = {}
    proof["pi_a"] = g1.zero()
    proof["pi_b"] = g2.zero()
    proof["pi_c"] = g1.zero()
    pib1 = g1.zero()

    for i in range(vk_proof["nVars"]):
        proof["pi_a"] = CurvePoint(g1, proof["pi_a"]) + CurvePoint(g1, mul_scalar(vk_proof["A"][i], witness[i]))
        proof["pi_b"] = CurvePoint(g2, proof["pi_b"]) + CurvePoint(g2, mul_scalar(vk_proof["B2"][i], witness[i]))
        pib1 = pib1 + CurvePoint(g1, mul_scalar(vk_proof["B1"][i], witness[i]))

    for i in range(vk_proof["nPublic"] + 1, vk_proof["nVars"]):
        proof["pi_c"] = CurvePoint(g1, proof["pi_c"]) + CurvePoint(g1, mul_scalar(vk_proof["C"][i], witness[i]))

    proof["pi_a"] = proof["pi_a"] + vk_proof["vk_alfa_1"]
    proof["pi_a"] = proof["pi_a"] + mul_scalar(vk_proof["vk_delta_1"], r)

    proof["pi_b"] = proof["pi_b"] + vk_proof["vk_beta_2"]
    proof["pi_b"] = proof["pi_b"] + mul_scalar(vk_proof["vk_delta_2"], s)

    pib1 = pib1 + vk_proof["vk_beta_1"]
    pib1 = pib1 + mul_scalar(vk_proof["vk_delta_1"], s)

    h = calculate_H(vk_proof, witness)

    for i in range(len(h)):
        proof["pi_c"] = CurvePoint(g1, proof["pi_c"]) + CurvePoint(g1, mul_scalar(vk_proof["hExps"][i], h[i]))
    proof["pi_c"] = proof["pi_c"] + mul_scalar(proof["pi_a"], s)
    proof["pi_c"] = proof["pi_c"] + mul_scalar(pib1, r)
    proof["pi_c"] = proof["pi_c"] + mul_scalar(vk_proof["vk_delta_1"], (r * s).neg())

    public_signals = witness[1:vk_proof["nPublic"]+1]

    proof["pi_a"] = proof["pi_a"].affine()
    proof["pi_b"] = proof["pi_b"].affine()
    proof["pi_c"] = proof["pi_c"].affine()
    proof["protocol"] = "groth"
    return (proof, public_signals)

def calculate_H(vk_proof, witness):
    pol = bn128_FieldPolynomial()
    m = vk_proof["domainSize"]
    polA_T = [PolField(0).zero()]*m
    polB_T = [PolField(0).zero()]*m

    for i in range(vk_proof["nVars"]):
        for c in vk_proof["polsA"][i]:
            polA_T[c] = polA_T[c] + (witness[i] * vk_proof["polsA"][i][c])
        for c in vk_proof["polsB"][i]:
            polB_T[c] = polB_T[c] + (witness[i] * vk_proof["polsB"][i][c])

    polA_S = pol.ifft(polA_T)
    polB_S = pol.ifft(polB_T)

    r = log2(m) + 1
    pol._set_roots(r)
    for i in range(len(polA_S)):
        polA_S[i] = polA_S[i] * pol.roots[r][i]
        polB_S[i] = polB_S[i] * pol.roots[r][i]

    polA_todd = pol.fft(polA_S)
    polB_todd = pol.fft(polB_S)
    polAB_T = [None] * len(polA_S) * 2
    for i in range(len(polA_S)):
        polAB_T[2*i] = polA_T[i] * polB_T[i]
        polAB_T[2*i+1] = polA_todd[i] * polB_todd[i]

    h_s = pol.ifft(polAB_T)
    h_s = h_s[m:]
    return h_s

if __name__ == "__main__":
    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.r1cs")
    gr.calc_polynomials()
    at_list = gr.calc_values_at_T()
    gr.calc_encrypted_values_at_T()

    wasm_path = os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.wasm"
    c = Calculator(wasm_path)
    witness = c.calculate({"a": 33, "b": 34})

    proof, publicSignals = gen_proof(gr.setup["vk_proof"], witness)