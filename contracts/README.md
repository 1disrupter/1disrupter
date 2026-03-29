# AlphaAI Smart Contract — Deployment Guide

## Contract: AlphaAIManager.sol
Manages strategies, investor balances, and capital allocation on Sepolia testnet.

## Prerequisites

Add these to `backend/.env`:
```
DEPLOYER_PRIVATE_KEY=0x...   # Private key with ~0.01 Sepolia ETH
SEPOLIA_RPC_URL=https://...  # Alchemy/Infura Sepolia endpoint
ETHERSCAN_API_KEY=...        # From https://etherscan.io/myapikey
CONTRACT_ADDRESS_SEPOLIA=    # Filled automatically after deploy
```

### Get Sepolia ETH
- https://cloud.google.com/application/web3/faucet/ethereum/sepolia
- https://sepoliafaucet.com

## Deployment

```bash
cd /app/contracts
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

Output:
- Contract address, TX hash, gas used, block number
- Saved to `deployments/sepolia/AlphaAIManager.json`
- Auto-updates `backend/.env` and `backend/web3/contract_abi.py`

## Verification

```bash
npx hardhat run scripts/verify.js --network sepolia
```

Retries 3x if Etherscan rate-limits. Verification status saved to deployment artifact.

## Testing via Stripe Dashboard (Webhook Events)

After deployment, test the full subscription lifecycle:

1. Go to **Stripe Dashboard → Developers → Webhooks**
2. Select your webhook endpoint
3. Click **"Send Test Event"**
4. Send each event type and verify:
   - `checkout.session.completed` → 200 OK, user activated
   - `customer.subscription.created` → user status = active/trialing
   - `customer.subscription.updated` → status synced
   - `customer.subscription.deleted` → user canceled, tier = free
   - `invoice.payment_succeeded` → subscription extended
   - `invoice.payment_failed` → user status = past_due
   - `charge.refunded` → user canceled (full refund)
   - `charge.dispute.created` → user flagged

## Admin Endpoints

```
GET /api/admin/contract/status?admin_key=alphaai_admin_2026
GET /api/contract/info
GET /api/contract/strategies
GET /api/contract/balance/{wallet_address}
```

## Architecture

```
contracts/
├── contracts/AlphaAIManager.sol   # Solidity source
├── scripts/deploy.js              # Deployment script
├── scripts/verify.js              # Etherscan verification
├── deployments/sepolia/           # Deployment artifacts
├── artifacts/                     # Compiled contracts
└── hardhat.config.js              # Hardhat config (reads backend/.env)

backend/
├── services/contract_manager.py   # Web3 integration layer (caching, fallback)
├── web3/contract_abi.py           # ABI + addresses
├── routes/web3_routes.py          # REST endpoints
└── routes/admin.py                # Admin contract/status endpoint
```
