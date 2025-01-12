// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FingerVeinAuth {
    struct BiometricData {
        bytes encryptedTemplate;
        address owner;
    }

    // Mapping to store biometric data by UID (instead of using msg.sender)
    mapping(string => BiometricData) public biometricTemplates;

    // Store user data for enrollment, using UID as key
    function enrollUser(string memory uid, bytes memory encryptedTemplate) public {
        // Check if the user is already enrolled with the same UID
        require(biometricTemplates[uid].owner == address(0), "User already enrolled");
        
        // Store the encrypted template under the provided UID
        biometricTemplates[uid] = BiometricData(encryptedTemplate, msg.sender);
    }

    // Authenticate user by comparing provided query template with stored template
    function authenticateUser(string memory uid, bytes memory queryTemplate) public view returns (bool) {
        // Retrieve the stored template using the provided UID
        BiometricData memory userTemplate = biometricTemplates[uid];
        
        // Ensure the user is enrolled with the given UID
        require(userTemplate.owner != address(0), "User not enrolled");

        // Compare the query template with the stored encrypted template
        return keccak256(userTemplate.encryptedTemplate) == keccak256(queryTemplate);
    }
}
