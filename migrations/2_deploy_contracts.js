const FingerVeinAuth = artifacts.require("FingerVeinAuth");

module.exports = function(deployer) {
  deployer.deploy(FingerVeinAuth);
};
