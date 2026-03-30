# AlphaAI Smart Contract - ABI for Web3 Integration (v2.0 — Performance Attestation)

ALPHA_AI_MANAGER_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "investor", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "InvestorDeposited",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "investor", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "InvestorWithdrawn",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "name", "type": "string"}
        ],
        "name": "StrategyAdded",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "StrategyAllocated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "StrategyDeallocated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"indexed": False, "internalType": "int256", "name": "sharpe", "type": "int256"},
            {"indexed": False, "internalType": "uint256", "name": "winRate", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "drawdown", "type": "uint256"},
            {"indexed": False, "internalType": "int256", "name": "monthlyPnl", "type": "int256"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "StrategyPerformanceUpdated",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "string", "name": "name", "type": "string"}],
        "name": "addStrategy",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "allocateToStrategy",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "contractVersion",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "deallocateFromStrategy",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "emergencyWithdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "investor", "type": "address"}],
        "name": "getInvestorBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "strategyId", "type": "uint256"}],
        "name": "getStrategy",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "strategyId", "type": "uint256"}],
        "name": "getStrategyPerformance",
        "outputs": [
            {
                "components": [
                    {"internalType": "int256", "name": "sharpe", "type": "int256"},
                    {"internalType": "uint256", "name": "winRate", "type": "uint256"},
                    {"internalType": "uint256", "name": "drawdown", "type": "uint256"},
                    {"internalType": "int256", "name": "monthlyPnl", "type": "int256"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
                ],
                "internalType": "struct AlphaAIManager.StrategyPerformance",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "investors",
        "outputs": [
            {"internalType": "uint256", "name": "balance", "type": "uint256"},
            {"internalType": "bool", "name": "active", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "performance",
        "outputs": [
            {"internalType": "int256", "name": "sharpe", "type": "int256"},
            {"internalType": "uint256", "name": "winRate", "type": "uint256"},
            {"internalType": "uint256", "name": "drawdown", "type": "uint256"},
            {"internalType": "int256", "name": "monthlyPnl", "type": "int256"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "strategies",
        "outputs": [
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "uint256", "name": "allocated", "type": "uint256"},
            {"internalType": "bool", "name": "active", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "strategyCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "strategyId", "type": "uint256"},
            {"internalType": "int256", "name": "sharpe", "type": "int256"},
            {"internalType": "uint256", "name": "winRate", "type": "uint256"},
            {"internalType": "uint256", "name": "drawdown", "type": "uint256"},
            {"internalType": "int256", "name": "monthlyPnl", "type": "int256"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "updateStrategyPerformance",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

ALPHA_AI_MANAGER_BYTECODE = "0x"

SEPOLIA_CONFIG = {
    "chain_id": 11155111,
    "rpc_url": "https://sepolia.infura.io/v3/",
    "explorer_url": "https://sepolia.etherscan.io",
    "name": "Sepolia Testnet"
}

CONTRACT_ADDRESSES = {
    "sepolia": None,
    "mainnet": None
}
