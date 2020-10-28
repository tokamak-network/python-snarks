import os
import json

from ..arithmetic import bn128_Field, bn128_FieldPolynomial, log2, mul_scalar, G1, G2, pairing, CurvePoint, PolField, F1_P, F12
from .groth_setup import Groth
from .groth_prover import gen_proof
from .witness_calculator import Calculator

def is_valid(vk_verifier, proof, public_signals):
    g1 = G1()
    g2 = G2()
    cpub = CurvePoint(g1, vk_verifier["IC"][0])
    for i in range(vk_verifier["nPublic"]):
        tmp1 = mul_scalar(CurvePoint(g1, vk_verifier["IC"][i+1]), public_signals[i])
        cpub = cpub + tmp1

    pair = pairing(proof["pi_a"], proof["pi_b"])
    tmp1 = F12(vk_verifier["vk_alfabeta_12"][0], vk_verifier["vk_alfabeta_12"][1])
    
    buf = pairing(cpub, vk_verifier["vk_gamma_2"])
    tmp2 = F12(buf[0], buf[1])

    buf = pairing(proof["pi_c"], vk_verifier["vk_delta_2"])
    tmp3 = F12(buf[0], buf[1])
    tmp = tmp1 * (tmp2 * tmp3)

    return pair == tmp

if __name__ == "__main__":
    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.r1cs")
    gr.calc_polynomials()
    at_list = gr.calc_values_at_T()
    gr.calc_encrypted_values_at_T()

    wasm_path = os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.wasm"
    c = Calculator(wasm_path)
    witness = c.calculate({"a": 33, "b": 34})

    proof, publicSignals = gen_proof(gr.setup["vk_proof"], witness)
    print("#"*80)
    print(proof)
    print("#"*80)
    print(publicSignals)
    print("#"*80)

    result = is_valid(gr.setup["vk_verifier"], proof, publicSignals)
    print(result)