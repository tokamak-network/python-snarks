import pytest
import os
from python_snarks import Groth, Calculator, gen_proof, is_valid

def test_groth():
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
    assert result == True