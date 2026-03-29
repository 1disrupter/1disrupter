/**
 * AlphaAI Manager — Verify on Etherscan
 *
 * Prerequisites:
 *   1. Contract deployed (deployments/sepolia/AlphaAIManager.json exists)
 *   2. ETHERSCAN_API_KEY in backend/.env
 *
 * Run:
 *   cd /app/contracts
 *   npx hardhat run scripts/verify.js --network sepolia
 */
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const deployPath = path.join(__dirname, "..", "deployments", "sepolia", "AlphaAIManager.json");

  if (!fs.existsSync(deployPath)) {
    console.error("No deployment artifact found. Run deploy.js first.");
    process.exit(1);
  }

  const deployment = JSON.parse(fs.readFileSync(deployPath, "utf8"));
  const address = deployment.address;

  console.log(`\n  Verifying AlphaAIManager at ${address} on Sepolia...\n`);

  const MAX_RETRIES = 3;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      await hre.run("verify:verify", {
        address,
        constructorArguments: [],
      });
      console.log(`\n  Verified!`);
      console.log(`  https://sepolia.etherscan.io/address/${address}#code\n`);

      // Update deployment artifact
      deployment.verified = true;
      deployment.verifiedAt = new Date().toISOString();
      fs.writeFileSync(deployPath, JSON.stringify(deployment, null, 2));
      return;
    } catch (e) {
      if (e.message.includes("Already Verified")) {
        console.log("  Contract is already verified.");
        deployment.verified = true;
        deployment.verifiedAt = deployment.verifiedAt || new Date().toISOString();
        fs.writeFileSync(deployPath, JSON.stringify(deployment, null, 2));
        return;
      }
      console.warn(`  Attempt ${attempt}/${MAX_RETRIES} failed: ${e.message}`);
      if (attempt < MAX_RETRIES) {
        console.log("  Retrying in 10s...");
        await new Promise((r) => setTimeout(r, 10000));
      }
    }
  }

  console.error("  Verification failed after all retries.");
  process.exit(1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
