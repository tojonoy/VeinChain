from flask import Flask, request, jsonify
from web3 import Web3
import json
from Crypto.Cipher import AES
import base64
from Crypto.Util.Padding import pad ,unpad
from flasgger import Swagger ,swag_from
import numpy as np
from PIL import Image
from skimage.exposure import equalize_adapthist
import io
from feature_extractor import extract_feature
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
swagger=Swagger(app)
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
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "string",
          "name": "uid",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "bool",
          "name": "exists",
          "type": "bool"
        },
        {
          "indexed": false,
          "internalType": "bytes",
          "name": "featureVector",
          "type": "bytes"
        }
      ],
      "name": "UserAuthenticated",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "string",
          "name": "uid",
          "type": "string"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        }
      ],
      "name": "UserEnrolled",
      "type": "event"
    },
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
          "internalType": "string",
          "name": "encryptedFeatureVector",
          "type": "string"
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
          "internalType": "string",
          "name": "encryptedFeatureVector",
          "type": "string"
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
        }
      ],
      "name": "authenticateUser",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    }
  ]''')

contract_address = "0xc9952216C577bd9BBB47b8dE11AA18Cb5Df2FB8a"  # Replace with your contract address
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Set up your account and private key
account = "0xb8272E3BAb9e740f74Cf688c77E952De52fCd512"  

# Set the private key (for signing transactions)
private_key = "0x70002d6af37bc76a698abd8f1e402f26744c1822daa0395ba69975817e5714eb"  # Replace with your private key from Ganache

aes_key = bytes.fromhex('603deb1015ca71be2b73aef0857d7781f19bff5a1b6a9d82e5a308d6d44323b1')
aes_iv = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
def float_to_fixed(value, scale=10**6):
    return int(value * scale)

key = [0xAB] * 128  # XOR encryption key

def xor_encrypt(data, key):
    scaled_data = np.array(data, dtype=np.uint)  # Enforce 8-bit integers
    print("Scaled Data:", scaled_data)  # Debugging output
    x=bytes([scaled_data[i] ^ key[i % len(key)] for i in range(len(scaled_data))])
    print(x)
    return x.hex()
def float_vector_to_bytes(vector):
    return np.array(vector, dtype=np.float32).flatten().tobytes()

def bytes_to_float_vector(byte_data):
    return np.frombuffer(byte_data, dtype=np.float32).flatten()

# AES encyrp method (keey keep same for encrypt and decrypt)

def encrypt_aes(data):
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return encrypted.hex()

def decrypt_aes(encrypted_data):
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    decrypted = unpad(cipher.decrypt(bytes.fromhex(encrypted_data)), AES.block_size)
    return decrypted
def preprocess_image(image, box=(280, 140, 410, 500), width=224, height=224):
 
    crop = image.crop(box)
    crop = crop.rotate(90, expand=True)
    crop = crop.resize((width, height))
  #clahe
    img_array = np.asarray(crop)
    clahe_img = equalize_adapthist(img_array, clip_limit=0.03)  # Adjust clip_limit as needed

    return clahe_img

# Route 1: Enroll User with UID and encrypted template
@app.route('/enroll', methods=['POST'])
@swag_from({
    "summary": "Enroll a user",
    "tags": ["User Enrollment"],
    "consumes": ["multipart/form-data"],
    "parameters": [
        {
            "name": "uid",
            "in": "formData",
            "required": True,
            "type": "string",
            "example": "user123"
        },
        {
            "name": "image",
            "in": "formData",
            "required": True,
            "type": "file"
        }
    ],
    "responses": {
        "200": {
            "description": "User successfully enrolled",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "User enrolled"},
                    "txHash": {"type": "string", "example": "0xabc123..."}
                }
            }
        },
        "400": {
            "description": "Error occurred",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "No image provided"}
                }
            }
        }
    }
})
def enroll_user():
    try:
        uid = request.form['uid']
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image_file = request.files['image']
        image = Image.open(io.BytesIO(image_file.read()))

        processed_image = preprocess_image(image)
        feature_vector = extract_feature(processed_image)  # 128 floating point values

        feature_bytes = float_vector_to_bytes(feature_vector)
        print("feature vector:",feature_vector.tolist())
        print("feature_bytes",feature_bytes)  # Convert float to bytes
        encrypted_template = encrypt_aes(feature_bytes)  # Encrypt bytes
        '''if isinstance(encrypted_template, str):  
          encrypted_template = encrypted_template.encode('utf-8')  # Ensure it's bytes'''
        print("encrypted_template:", encrypted_template)
        transaction = contract.functions.enrollUser(uid, encrypted_template).build_transaction({
            'chainId': 1337,
            'gas': 6721975,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': web3.eth.get_transaction_count(account),
        })

        signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)

        return jsonify({"status": "User enrolled", "txHash": tx_hash.hex(),"feature vector":encrypted_template}), 200

    except Exception as e:
        return {"error": str(e)}, 400

# Route 2: Authenticate User with UID and query template
@app.route('/authenticate', methods=['POST'])
@swag_from({
    "summary": "Authenticate a user",
    "tags": ["User Authentication"],
    "consumes": ["multipart/form-data"],
    "parameters": [
        {
            "name": "uid",
            "in": "formData",
            "required": True,
            "type": "string",
            "example": "user123"
        },
        {
            "name": "image",
            "in": "formData",
            "required": True,
            "type": "file"
        }
    ],
    "responses": {
        "200": {
            "description": "Authentication result",
            "schema": {
                "type": "object",
                "properties": {
                    "authenticationResult": {"type": "string", "example": "User authenticated successfully"}
                }
            }
        },
        "400": {
            "description": "Error occurred",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "No image provided"}
                }
            }
        }
    }
})
def authenticate_user():
    try:
        uid = request.form['uid']
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image_file = request.files['image']
        image = Image.open(io.BytesIO(image_file.read()))

        processed_image = preprocess_image(image)
        feature_vector = extract_feature(processed_image)
        print("Feature Vector auth :", feature_vector.tolist())

        is_enrolled, encrypted_stored_template = contract.functions.authenticateUser(uid).call()

        if not is_enrolled:
            return jsonify({"authenticationResult": "User does not exist"}), 400
        print("encrypted_stored_template:", encrypted_stored_template)
        stored_feature_bytes = decrypt_aes(encrypted_stored_template)  # Decrypt bytes
        stored_feature_vector = bytes_to_float_vector(stored_feature_bytes) 
         # Convert to float vector
        print("stored_feature_bytes:", stored_feature_bytes)
        print("stored_feature_vector:", stored_feature_vector.tolist()) 
        similarity_score = np.dot(feature_vector, stored_feature_vector) / (np.linalg.norm(feature_vector) * np.linalg.norm(stored_feature_vector)) * 100
        print("Similarity score:", similarity_score)
        if similarity_score >= 92:
            return jsonify({"authenticationResult": "User authenticated successfully"}), 200
        else:
            return jsonify({"authenticationResult": "Authentication failed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
