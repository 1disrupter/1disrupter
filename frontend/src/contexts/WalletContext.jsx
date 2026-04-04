import { useState, createContext, useContext } from "react";

/**
 * WalletContext — Stubbed for SaaS-only launch.
 * Phase 2 Web3 will restore full ethers.js integration.
 * All consumers (useWallet) receive safe null/no-op values.
 */
const WalletContext = createContext();

export const useWallet = () => useContext(WalletContext);

export const WalletProvider = ({ children }) => {
  const [wallet] = useState(null);
  const [investor] = useState(null);
  const [loading] = useState(false);
  const [chainId] = useState(null);
  const [ethBalance] = useState(null);

  const connectWallet = async () => {};
  const disconnectWallet = () => {};
  const refreshInvestor = async () => {};
  const switchToSepolia = async () => {};

  const isOnSepolia = false;

  return (
    <WalletContext.Provider value={{
      wallet, investor, loading, connectWallet, disconnectWallet,
      refreshInvestor, chainId, ethBalance, switchToSepolia, isOnSepolia
    }}>
      {children}
    </WalletContext.Provider>
  );
};
