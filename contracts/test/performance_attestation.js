const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AlphaAIManager — Performance Attestation", function () {
  let contract, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("AlphaAIManager");
    contract = await Factory.deploy();
    await contract.waitForDeployment();
    // Add a strategy for testing
    await contract.addStrategy("BTC Momentum Alpha");
  });

  describe("contractVersion", function () {
    it("returns 2.0-performance-attestation", async function () {
      expect(await contract.contractVersion()).to.equal("2.0-performance-attestation");
    });
  });

  describe("updateStrategyPerformance", function () {
    it("stores performance metrics on-chain", async function () {
      const ts = Math.floor(Date.now() / 1000);
      await contract.updateStrategyPerformance(0, 241, 6750, 1230, -350, ts);

      const perf = await contract.getStrategyPerformance(0);
      expect(perf.sharpe).to.equal(241);
      expect(perf.winRate).to.equal(6750);
      expect(perf.drawdown).to.equal(1230);
      expect(perf.monthlyPnl).to.equal(-350);
      expect(perf.timestamp).to.equal(ts);
    });

    it("emits StrategyPerformanceUpdated event", async function () {
      const ts = Math.floor(Date.now() / 1000);
      await expect(contract.updateStrategyPerformance(0, 100, 5000, 800, 200, ts))
        .to.emit(contract, "StrategyPerformanceUpdated")
        .withArgs(0, 100, 5000, 800, 200, ts);
    });

    it("overwrites previous performance data", async function () {
      const ts1 = Math.floor(Date.now() / 1000);
      await contract.updateStrategyPerformance(0, 100, 5000, 800, 200, ts1);
      const ts2 = ts1 + 86400;
      await contract.updateStrategyPerformance(0, 300, 7500, 500, 450, ts2);

      const perf = await contract.getStrategyPerformance(0);
      expect(perf.sharpe).to.equal(300);
      expect(perf.winRate).to.equal(7500);
      expect(perf.timestamp).to.equal(ts2);
    });

    it("handles negative sharpe and pnl values", async function () {
      const ts = Math.floor(Date.now() / 1000);
      await contract.updateStrategyPerformance(0, -150, 3000, 2500, -800, ts);

      const perf = await contract.getStrategyPerformance(0);
      expect(perf.sharpe).to.equal(-150);
      expect(perf.monthlyPnl).to.equal(-800);
    });

    it("works for multiple strategies", async function () {
      await contract.addStrategy("ETH Mean Reversion");
      const ts = Math.floor(Date.now() / 1000);

      await contract.updateStrategyPerformance(0, 241, 6750, 1230, 500, ts);
      await contract.updateStrategyPerformance(1, 180, 5500, 1800, -200, ts);

      const perf0 = await contract.getStrategyPerformance(0);
      const perf1 = await contract.getStrategyPerformance(1);
      expect(perf0.sharpe).to.equal(241);
      expect(perf1.sharpe).to.equal(180);
    });
  });

  describe("access control", function () {
    it("reverts when non-owner calls updateStrategyPerformance", async function () {
      const ts = Math.floor(Date.now() / 1000);
      await expect(
        contract.connect(other).updateStrategyPerformance(0, 100, 5000, 800, 200, ts)
      ).to.be.revertedWith("Not authorized");
    });
  });

  describe("getStrategyPerformance", function () {
    it("returns zeroes for strategy with no performance set", async function () {
      const perf = await contract.getStrategyPerformance(99);
      expect(perf.sharpe).to.equal(0);
      expect(perf.winRate).to.equal(0);
      expect(perf.timestamp).to.equal(0);
    });
  });

  // Sanity: existing features still work
  describe("existing features", function () {
    it("deposit and withdraw still work", async function () {
      await contract.deposit({ value: ethers.parseEther("1.0") });
      const bal = await contract.getInvestorBalance(owner.address);
      expect(bal).to.equal(ethers.parseEther("1.0"));
    });

    it("strategy allocation still works", async function () {
      await contract.allocateToStrategy(0, 1000);
      const [name, allocated, active] = await contract.getStrategy(0);
      expect(name).to.equal("BTC Momentum Alpha");
      expect(allocated).to.equal(1000);
      expect(active).to.equal(true);
    });
  });
});
