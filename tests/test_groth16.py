import pytest
import os
from python_snarks import Groth, Calculator, gen_proof, is_valid

def test_groth():
    ## 1. setup zkp
    print("1. setting up...")
    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.r1cs")
    gr.setup_zk()
    gr.export_solidity_verifier("verifier.sol")

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
'''
from web3 import Web3, HTTPProvider    
import json

def __get_compiled_contract(contract_path):
    with open(contract_path, "r", encoding="utf-8") as f:
        return json.load(f)
    return None

def send_raw_transaction(w3, unsigned_tx, account):
    unsigned_tx.update({"gas" : 6000000})
    unsigned_tx.update({"gasPrice" : int(1e9)})
    unsigned_tx.update({"nonce" : w3.eth.getTransactionCount(account)})
    signed_tx = w3.eth.account.signTransaction(unsigned_tx, "7a25c53591e31bdc99d76e7f2e192c34c0320b7d687904495a913ea0fdb17eb7")
    
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f"tx : {tx_hash.hex()}")
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_hash, tx_receipt

def deploy(w3):
    contract_data = __get_compiled_contract("tests/Verifier.json")

    unsigned_tx = w3.eth.contract(
        abi=contract_data["abi"],
        bytecode=contract_data["bytecode"]).constructor().buildTransaction()
    tx_hash, tx_receipt = send_raw_transaction(w3, unsigned_tx, "0xCe1d2141A6C04126cD0F5d650b7EB8D5E5506DF6")

    return tx_receipt["contractAddress"]

def get_contract_instance(w3, contract_address, contract_path):
    contract_data = __get_compiled_contract(contract_path)
    instance = w3.eth.contract(
        address=contract_address,
        abi=contract_data["abi"])
    return instance    

# test Verifier contract
# TODO: automate all process. use test toolchain
def test_solidity():
    w3 = Web3(HTTPProvider("HTTP://127.0.0.1:7545"))
    contract_address = deploy(w3)
    contract_instance = get_contract_instance(w3, contract_address, "tests/Verifier.json")

    ## 1. setup zkp
    print("1. setting up...")
    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/circuit/circuit.r1cs")
    gr.setup_zk()
    gr.export_solidity_verifier("verifier.sol")

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
    inputs = [[int(str(proof["pi_a"][0])), int(str(proof["pi_a"][1]))],
        [[int(str(proof["pi_b"][0][1])), int(str(proof["pi_b"][0][0]))], [int(str(proof["pi_b"][1][1])), int(str(proof["pi_b"][1][0]))]],
        [int(str(proof["pi_c"][0])), int(str(proof["pi_c"][1]))]]
    print(inputs)
    result = contract_instance.functions.verifyProof(
        [int(str(proof["pi_a"][0])), int(str(proof["pi_a"][1]))],
        [[int(str(proof["pi_b"][0][1])), int(str(proof["pi_b"][0][0]))], [int(str(proof["pi_b"][1][1])), int(str(proof["pi_b"][1][0]))]],
        [int(str(proof["pi_c"][0])), int(str(proof["pi_c"][1]))],
        [int(str(publicSignals[0]))]
    ).call()
    assert result == True
'''