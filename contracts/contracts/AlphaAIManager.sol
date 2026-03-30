// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AlphaAIManager {
    
    address public owner;

    struct Investor {
        uint256 balance;
        bool active;
    }

    struct Strategy {
        string name;
        uint256 allocated;
        bool active;
    }

    struct StrategyPerformance {
        int256 sharpe;       // scaled x100 (e.g. 241 = 2.41)
        uint256 winRate;     // scaled x100 (e.g. 6750 = 67.50%)
        uint256 drawdown;    // scaled x100 (e.g. 1230 = 12.30%)
        int256 monthlyPnl;   // scaled x100 (e.g. -350 = -3.50%)
        uint256 timestamp;
    }

    mapping(address => Investor) public investors;
    mapping(uint256 => Strategy) public strategies;
    mapping(uint256 => StrategyPerformance) public performance;
    uint256 public strategyCount;

    event InvestorDeposited(address indexed investor, uint256 amount);
    event InvestorWithdrawn(address indexed investor, uint256 amount);
    event StrategyAdded(uint256 indexed strategyId, string name);
    event StrategyAllocated(uint256 indexed strategyId, uint256 amount);
    event StrategyDeallocated(uint256 indexed strategyId, uint256 amount);
    event StrategyPerformanceUpdated(
        uint256 indexed strategyId,
        int256 sharpe,
        uint256 winRate,
        uint256 drawdown,
        int256 monthlyPnl,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function contractVersion() public pure returns (string memory) {
        return "2.0-performance-attestation";
    }

    /*** Investor Functions ***/
    function deposit() external payable {
        require(msg.value > 0, "Deposit > 0 required");
        Investor storage inv = investors[msg.sender];
        inv.balance += msg.value;
        inv.active = true;
        emit InvestorDeposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        Investor storage inv = investors[msg.sender];
        require(inv.balance >= amount, "Insufficient balance");
        inv.balance -= amount;
        if(inv.balance == 0) inv.active = false;
        payable(msg.sender).transfer(amount);
        emit InvestorWithdrawn(msg.sender, amount);
    }

    /*** Strategy Functions ***/
    function addStrategy(string calldata name) external onlyOwner {
        strategies[strategyCount] = Strategy(name, 0, true);
        emit StrategyAdded(strategyCount, name);
        strategyCount++;
    }

    function allocateToStrategy(uint256 strategyId, uint256 amount) external onlyOwner {
        Strategy storage strat = strategies[strategyId];
        require(strat.active, "Strategy not active");
        strat.allocated += amount;
        emit StrategyAllocated(strategyId, amount);
    }

    function deallocateFromStrategy(uint256 strategyId, uint256 amount) external onlyOwner {
        Strategy storage strat = strategies[strategyId];
        require(strat.allocated >= amount, "Not enough allocated");
        strat.allocated -= amount;
        emit StrategyDeallocated(strategyId, amount);
    }

    /*** Performance Attestation ***/
    function updateStrategyPerformance(
        uint256 strategyId,
        int256 sharpe,
        uint256 winRate,
        uint256 drawdown,
        int256 monthlyPnl,
        uint256 timestamp
    ) external onlyOwner {
        performance[strategyId] = StrategyPerformance(
            sharpe, winRate, drawdown, monthlyPnl, timestamp
        );
        emit StrategyPerformanceUpdated(
            strategyId, sharpe, winRate, drawdown, monthlyPnl, timestamp
        );
    }

    function getStrategyPerformance(uint256 strategyId)
        external
        view
        returns (StrategyPerformance memory)
    {
        return performance[strategyId];
    }

    /*** Utility Functions ***/
    function getInvestorBalance(address investor) external view returns (uint256) {
        return investors[investor].balance;
    }

    function getStrategy(uint256 strategyId) external view returns (string memory, uint256, bool) {
        Strategy storage strat = strategies[strategyId];
        return (strat.name, strat.allocated, strat.active);
    }

    function emergencyWithdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
