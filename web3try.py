from web3 import Web3
import json

# Connect to Ganache (replace with the appropriate URL if you're using another network)
ganache_url = "http://127.0.0.1:7545"  # Default Ganache URL
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Make sure you are connected
if not web3.is_connected():
    print("Failed to connect to the network.")
    exit()

# Contract ABI (replace this with your contract's ABI)
contract_abi = json.loads(
    '''[
    {
      "inputs": [],
      "name": "receivedData",
      "outputs": [
        {
          "internalType": "bytes",
          "name": "",
          "type": "bytes"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "bytes",
          "name": "data",
          "type": "bytes"
        }
      ],
      "name": "receiveData",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getData",
      "outputs": [
        {
          "internalType": "bytes",
          "name": "",
          "type": "bytes"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    }
  ]'''
)  # Replace with the actual ABI of your contract

# Contract address (replace with the address from your deployment)
contract_address = "0x5C126bF3Da8638C2f835ff77A043E46c4Cb6B11d"

# Create the contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Set the account to use for transactions (replace with your Ganache account address)
account = "0x9f409a9B6497b34F2D1719198c127087d1e53424"  # Your Ganache account address

# Set the private key (for signing transactions)
private_key = "0x9fdad94c7854d069334092b0d3e993b6c4f026bec80a2bafe470411bd2721c5f"  # Replace with your private key from Ganache

# Send data to the contract
def send_data(data):
    # Build the transaction
    transaction = contract.functions.receiveData(data.encode()).build_transaction({
        'chainId': 1337,  # Network ID for Ganache
        'gas': 6721975,    # Gas limit
        'gasPrice': web3.to_wei('20', 'gwei'),
        'nonce': web3.eth.get_transaction_count(account),
    })

    # Sign the transaction
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
    return tx_hash
# Get the stored data from the contract
def get_data():
    data = contract.functions.getData().call()
    return data.decode()  # Decode bytes to string

# Send data (e.g., your name)
tx_hash=send_data("Thomas J")

# Wait for the transaction to be mined
web3.eth.wait_for_transaction_receipt(web3.to_hex(tx_hash))

# Retrieve the stored data
stored_data = get_data()
print(f"Stored data: {stored_data}")
