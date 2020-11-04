import pytest
import os
from python_snarks import Groth, Calculator, gen_proof, is_valid

def test_groth():
    ## 1. setup zkp
    print("1. setting up...")
    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.r1cs")
    gr.setup_zk()

    ## 2. proving
    print("2. proving...")
    wasm_path = os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.wasm"
    c = Calculator(wasm_path)
    witness = c.calculate({"a": 33, "b": 34})
    proof, publicSignals = gen_proof(gr.setup["vk_proof"], witness)
    print("#"*80)
    print(proof)
    print("#"*80)
    print(publicSignals)
    print("#"*80)

    ## 3. verifying
    print("3. verifying...")
    result = is_valid(gr.setup["vk_verifier"], proof, publicSignals)
    print(result)
    assert result == True
