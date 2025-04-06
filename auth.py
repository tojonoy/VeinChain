import os
import requests
import re

# Set API URL
ENROLL_API_URL = "http://127.0.0.1:8000/authenticate"  # Change if hosted elsewhere

# Path to `FV1_Test` directory
FV_TRAIN_DIR = "/Users/hp/FV1_Test"

TP = 0  # True Positives
FP = 0  # False Positives
TN = 0  # False Negatives

total_auth_time = 0  # Cumulative authentication time
total_gas_used = 0   # Cumulative gas usage
auth_attempts = 0    # Count of authentication attempts
FN = 0  # False Negatives
# Iterate through each subfolder (UIDs)
for uid in sorted(os.listdir(FV_TRAIN_DIR)):  
    subfolder_path = os.path.join(FV_TRAIN_DIR, uid)

    # Ensure it's a directory
    if os.path.isdir(subfolder_path):
        # Check for a valid image inside the folder
        image_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith((".bmp", ".png", ".jpg", ".jpeg"))]

        if image_files:
            image_path = os.path.join(subfolder_path, image_files[0])  # Take the first image
            print(f"Authenticating UID: {uid} with Image: {image_files[0]}")

            # Send API request
            with open(image_path, "rb") as image_file:
                response = requests.post(
                    ENROLL_API_URL, 
                    files={"image": image_file},
                    data={"uid": uid}
                )

            if response.status_code == 200:
                response_json = response.json()
                auth_result = response_json.get("authenticationResult", "")
                auth_time_str = response_json.get("time", "0").split()[0]  # Extract only the number
                auth_time = float(auth_time_str)  # Convert to float
                gas_used = int(response_json.get("gasUsed", 0))  # Extract gas usage

                # Update cumulative metrics
                total_auth_time += auth_time
                total_gas_used += gas_used
                auth_attempts += 1

                # Extract User ID from response
                match = re.search(r"User:(\d+)", auth_result)
                if match:
                    user_id = match.group(1)  # Extracted user ID as a string
                    print(f"Extracted User ID: {user_id}")

                    if uid == user_id:
                        TP += 1
                        print(f"✅ Authenticated: {uid}")
                    
                # Display time and gas details
                print(f"🕒 Authentication Time: {auth_time:.4f} seconds")
                print(f"⛽ Gas Used: {gas_used}\n")

            else:
                FN += 1
                print(f"❌ Authentication failed for UID: {uid}, Status Code: {response.status_code}")

# Calculate cumulative averages
avg_auth_time = total_auth_time / auth_attempts if auth_attempts else 0
avg_gas_used = total_gas_used / auth_attempts if auth_attempts else 0

# Final metrics display
print("\n===== FINAL METRICS =====")
print(f"✅ True Positive (TP): {TP}")
print(f"❌ False Positive (FP): {FP}")
print(f"❌ False Negative (FN): {FN}")
print(f"🕒 Average Authentication Time: {avg_auth_time:.4f} seconds")
print(f"⛽ Average Gas Used: {avg_gas_used:.2f}")
print("=========================\n")
