import os
import requests

# Set API URL
ENROLL_API_URL = "http://127.0.0.1:8000/enroll"  # Change if hosted elsewhere

# Path to `FV1_Train` directory
FV_TRAIN_DIR = "/Users/hp/FV1_Train"

# Iterate through each subfolder (UIDs)
for uid in sorted(os.listdir(FV_TRAIN_DIR)):  
    subfolder_path = os.path.join(FV_TRAIN_DIR, uid)

    # Ensure it's a directory
    if os.path.isdir(subfolder_path):
        # Check for a valid image inside the folder
        image_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith((".bmp", ".png", ".jpg", ".jpeg"))]

        if image_files:
            image_path = os.path.join(subfolder_path, image_files[0])  # Take the first image
            print(f"Enrolling UID: {uid} with Image: {image_files[0]}")

            # Debug: Print the exact data being sent
            print(f"Sending Data: UID = {uid}, Image = {image_path}")

            # Send API request
            with open(image_path, "rb") as image_file:
                response = requests.post(
                    ENROLL_API_URL, 
                    files={"image": image_file}, 
                    data={"uid": str(uid)}  # Ensure UID is sent as a string
                )

            # Print response
            print("Response Status:", response.status_code)
            print("Response JSON:", response.json())

        else:
            print(f"No image found in folder: {uid}")
