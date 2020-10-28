# python-snarks

This is a Python implementation of zkSNARK schemes. This library is based on [snarkjs](https://github.com/iden3/snarkjs), and uses the output from [circom](https://github.com/iden3/circom).

For now, it is for research purpose, not implemented for product.

# Install dependencies
```
$ pip install cached_property
$ pip install wasmer==1.0.0a3
$ pip install wasmer_compiler_cranelift==1.0.0a3
```

# Run

```
$ python -m python-snark.groth16.groth_setup
$ python -m python-snark.groth16.groth_verifier
$ python -m python-snark.groth16.groth_prover
```

# Supported platforms

The supported platforms currently support are set to the requirements of the [wasmer-python](https://github.com/wasmerio/wasmer-python).

# TODO

* Compatibility with the latest snarkjs, circom
* Performance optimizing