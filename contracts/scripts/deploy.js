/**
 * AlphaAI Manager — Deploy to Sepolia
 *
 * Prerequisites:
 *   1. Add to backend/.env:
 *        DEPLOYER_PRIVATE_KEY=0x...  (funded with ~0.01 Sepolia ETH)
 *        SEPOLIA_RPC_URL=https://...  (Alchemy/Infura Sepolia endpoint)
 *   2. Compile: npx hardhat compile
 *
 * Run:
 *   cd /app/contracts
 *   npx hardhat run scripts/deploy.js --network sepolia
 */
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const network = hre.network.name;

  // Safety: block mainnet
  if (network === "mainnet" || network === "homestead") {
    console.error("ABORT: mainnet deployment blocked. Use sepolia only.");
    process.exit(1);
  }

  console.log(`\n  Deploying AlphaAIManager to ${network}...\n`);

  // Validate RPC connectivity
  const provider = hre.ethers.provider;
  try {
    const blockNumber = await provider.getBlockNumber();
    console.log(`  RPC connected — latest block: ${blockNumber}`);
  } catch (e) {
    console.error(`  RPC connection failed: ${e.message}`);
    process.exit(1);
  }

  const [deployer] = await hre.ethers.getSigners();
  const balance = await provider.getBalance(deployer.address);
  console.log(`  Deployer: ${deployer.address}`);
  console.log(`  Balance:  ${hre.ethers.formatEther(balance)} ETH\n`);

  if (balance === 0n) {
    console.error("  ABORT: deployer has 0 ETH. Fund the wallet first.");
    process.exit(1);
  }

  // Deploy
  const Factory = await hre.ethers.getContractFactory("AlphaAIManager");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  const tx = contract.deploymentTransaction();
  const receipt = await tx.wait();

  console.log(`  Contract deployed!`);
  console.log(`  Address:      ${address}`);
  console.log(`  TX Hash:      ${tx.hash}`);
  console.log(`  Block:        ${receipt.blockNumber}`);
  console.log(`  Gas Used:     ${receipt.gasUsed.toString()}`);
  console.log(`  Explorer:     https://sepolia.etherscan.io/address/${address}\n`);

  // Save deployment artifact
  const artifact = {
    address,
    deployer: deployer.address,
    network,
    chainId: 11155111,
    txHash: tx.hash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString(),
    deployedAt: new Date().toISOString(),
    verified: false,
    explorerUrl: `https://sepolia.etherscan.io/address/${address}`,
  };

  const deployDir = path.join(__dirname, "..", "deployments", "sepolia");
  fs.mkdirSync(deployDir, { recursive: true });
  fs.writeFileSync(
    path.join(deployDir, "AlphaAIManager.json"),
    JSON.stringify(artifact, null, 2)
  );
  console.log(`  Artifact saved to deployments/sepolia/AlphaAIManager.json`);

  // Update backend CONTRACT_ADDRESSES
  const backendConfigPath = path.join(__dirname, "..", "..", "backend", "web3", "contract_abi.py");
  if (fs.existsSync(backendConfigPath)) {
    let content = fs.readFileSync(backendConfigPath, "utf8");
    content = content.replace(
      /"sepolia": None/,
      `"sepolia": "${address}"`
    );
    fs.writeFileSync(backendConfigPath, content);
    console.log(`  Updated backend CONTRACT_ADDRESSES["sepolia"]`);
  }

  // Add CONTRACT_ADDRESS_SEPOLIA to backend/.env
  const envPath = path.join(__dirname, "..", "..", "backend", ".env");
  if (fs.existsSync(envPath)) {
    let envContent = fs.readFileSync(envPath, "utf8");
    if (envContent.includes("CONTRACT_ADDRESS_SEPOLIA=")) {
      envContent = envContent.replace(/CONTRACT_ADDRESS_SEPOLIA=.*/, `CONTRACT_ADDRESS_SEPOLIA=${address}`);
    } else {
      envContent += `\nCONTRACT_ADDRESS_SEPOLIA=${address}\n`;
    }
    fs.writeFileSync(envPath, envContent);
    console.log(`  Updated backend/.env CONTRACT_ADDRESS_SEPOLIA`);
  }

  console.log(`\n  Next step: npx hardhat run scripts/verify.js --network sepolia\n`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
