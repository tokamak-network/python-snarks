# python-snarks

This is a Python implementation of zkSNARK schemes. This library is based on [snarkjs](https://github.com/iden3/snarkjs), and uses the output from [circom](https://github.com/iden3/circom).

For now, it is for research purpose, not implemented for product.

# Install
```
$ pip install python-snarks
```

# Usage
```python
import os
from python_snarks import Groth, Calculator, gen_proof, is_valid

def test_groth():
    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.r1cs")
    gr.calc_polynomials()
    at_list = gr.calc_values_at_T()
    gr.calc_encrypted_values_at_T()

    # Calculate witness
    wasm_path = os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.wasm"
    c = Calculator(wasm_path)
    witness = c.calculate({"a": 33, "b": 34})

    # Generate proof
    proof, publicSignals = gen_proof(gr.setup["vk_proof"], witness)
    print("#"*80)
    print(proof)
    print("#"*80)
    print(publicSignals)
    print("#"*80)

    result = is_valid(gr.setup["vk_verifier"], proof, publicSignals)
    print(result)
    assert result == True
```

# Test

```
$ pytest tests/test_groth16.py
```

# Supported platforms

The supported platforms currently support are set to the requirements of the [wasmer-python](https://github.com/wasmerio/wasmer-python).

# TODO

* Compatibility with the latest snarkjs, circom
* Performance optimizing
