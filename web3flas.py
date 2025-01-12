from flask import Flask, request, jsonify
from web3 import Web3
import json
from Crypto.Cipher import AES
import base64
from Crypto.Util.Padding import pad

app = Flask(__name__)

# Connect to Ganache (or another Ethereum node)
ganache_url = "http://127.0.0.1:7545"  # Ganache default URL
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check if connected to the network
if not web3.is_connected():
    print("Failed to connect to the network.")
    exit()

# Contract ABI (replace with actual ABI)
contract_abi = json.loads('''
 [
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "name": "biometricTemplates",
      "outputs": [
        {
          "internalType": "bytes",
          "name": "encryptedTemplate",
          "type": "bytes"
        },
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "uid",
          "type": "string"
        },
        {
          "internalType": "bytes",
          "name": "encryptedTemplate",
          "type": "bytes"
        }
      ],
      "name": "enrollUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "uid",
          "type": "string"
        },
        {
          "internalType": "bytes",
          "name": "queryTemplate",
          "type": "bytes"
        }
      ],
      "name": "authenticateUser",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    }
  ]''')

# Contract address (replace with the actual deployed address)
contract_address = "0xe1c7A005Fc63591B524b149f74e645beBD812C12"  # Replace with your contract address

# Create the contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Set up your account and private key
account = "0x9f409a9B6497b34F2D1719198c127087d1e53424"  # Your Ganache account address

# Set the private key (for signing transactions)
private_key = "0x9fdad94c7854d069334092b0d3e993b6c4f026bec80a2bafe470411bd2721c5f"  # Replace with your private key from Ganache

aes_key = bytes.fromhex('603deb1015ca71be2b73aef0857d7781f19bff5a1b6a9d82e5a308d6d44323b1')
aes_iv = bytes.fromhex('000102030405060708090a0b0c0d0e0f')

# AES encryption method (use the same key and IV for both encryption and decryption)
def encrypt_aes(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted).decode('utf-8')

# Route 1: Enroll User with UID and encrypted template
@app.route('/enroll', methods=['POST'])
def enroll_user():
    try:
        # Get UID and plain biometric data from the request
        uid = request.json['uid']
        plain_template = request.json['template']
        
        # Encrypt the template (using the hardcoded AES key and IV)
        encrypted_template = encrypt_aes(plain_template, aes_key, aes_iv)
        
        # Call the contract to enroll the user with UID and encrypted template
        transaction = contract.functions.enrollUser(uid, encrypted_template.encode('utf-8')).build_transaction({
            'chainId': 1337,  # Ganache default chainId
            'gas': 6721975,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': web3.eth.get_transaction_count(account),
        })

        signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)

        return jsonify({"status": "User enrolled", "txHash": tx_hash.hex()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Route 2: Authenticate User with UID and query template
@app.route('/authenticate', methods=['POST'])
def authenticate_user():
    try:
        # Get UID and plain biometric query data from the request
        uid = request.json['uid']
        plain_query_template = request.json['queryTemplate']
        
        # Encrypt the query template (using the hardcoded AES key and IV)
        encrypted_query_template = encrypt_aes(plain_query_template, aes_key, aes_iv)
        
        # Call the contract to authenticate the user with UID and encrypted query template
        is_authenticated = contract.functions.authenticateUser(uid, encrypted_query_template.encode('utf-8')).call()

        return jsonify({"authenticationResult": is_authenticated}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
