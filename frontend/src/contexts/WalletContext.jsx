import { useState, useEffect, createContext, useContext } from "react";
import axios from "axios";
import { toast } from "sonner";
import { ethers } from "ethers";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sepolia Chain Config
const SEPOLIA_CHAIN_ID = "0xaa36a7"; // 11155111 in hex
const SEPOLIA_CONFIG = {
  chainId: SEPOLIA_CHAIN_ID,
  chainName: "Sepolia Testnet",
  nativeCurrency: { name: "SepoliaETH", symbol: "ETH", decimals: 18 },
  rpcUrls: ["https://rpc.sepolia.org"],
  blockExplorerUrls: ["https://sepolia.etherscan.io"]
};

const WalletContext = createContext();

export const useWallet = () => useContext(WalletContext);

export const WalletProvider = ({ children }) => {
  const [wallet, setWallet] = useState(null);
  const [investor, setInvestor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [ethBalance, setEthBalance] = useState(null);
  const [contractAddress, setContractAddress] = useState(null);

  // Check if already connected on mount
  useEffect(() => {
    const checkConnection = async () => {
      if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          await connectWallet();
        }
      }
    };
    checkConnection();

    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) {
          disconnectWallet();
        } else {
          setWallet(accounts[0]);
          updateBalance(accounts[0]);
        }
      });
      window.ethereum.on('chainChanged', () => window.location.reload());
    }

    // Fetch contract address
    axios.get(`${API}/contract/info`).then(res => {
      if (res.data.contract_address) setContractAddress(res.data.contract_address);
    }).catch(console.error);
  }, []);

  const updateBalance = async (address) => {
    if (provider && address) {
      try {
        const balance = await provider.getBalance(address);
        setEthBalance(ethers.utils.formatEther(balance));
      } catch (e) {
        console.error("Balance fetch error:", e);
      }
    }
  };

  const switchToSepolia = async () => {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: SEPOLIA_CHAIN_ID }]
      });
      return true;
    } catch (switchError) {
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [SEPOLIA_CONFIG]
          });
          return true;
        } catch (addError) {
          console.error("Failed to add Sepolia:", addError);
          return false;
        }
      }
      console.error("Failed to switch network:", switchError);
      return false;
    }
  };

  const connectWallet = async () => {
    setLoading(true);
    try {
      if (typeof window.ethereum !== 'undefined') {
        // Request accounts
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const address = accounts[0];
        
        // Setup provider and signer
        const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
        const web3Signer = web3Provider.getSigner();
        const network = await web3Provider.getNetwork();
        
        setProvider(web3Provider);
        setSigner(web3Signer);
        setChainId(network.chainId);
        setWallet(address);
        
        // Get ETH balance
        const balance = await web3Provider.getBalance(address);
        setEthBalance(ethers.utils.formatEther(balance));
        
        // Register with backend
        const response = await axios.post(`${API}/investors/register`, { wallet_address: address });
        setInvestor(response.data);
        
        // Check if on Sepolia
        if (network.chainId !== 11155111) {
          toast.warning("Please switch to Sepolia testnet for full functionality");
        } else {
          toast.success("MetaMask connected to Sepolia!");
        }
      } else {
        toast.error("MetaMask not detected. Please install MetaMask.");
      }
    } catch (error) {
      console.error("Wallet connection error:", error);
      if (error.code === 4001) {
        toast.error("Connection rejected by user");
      } else {
        toast.error("Failed to connect wallet");
      }
    }
    setLoading(false);
  };

  const disconnectWallet = () => {
    setWallet(null);
    setInvestor(null);
    setProvider(null);
    setSigner(null);
    setChainId(null);
    setEthBalance(null);
    toast.info("Wallet disconnected");
  };

  const refreshInvestor = async () => {
    if (wallet) {
      try {
        const response = await axios.get(`${API}/investors/${wallet}`);
        setInvestor(response.data);
        if (provider) {
          const balance = await provider.getBalance(wallet);
          setEthBalance(ethers.utils.formatEther(balance));
        }
      } catch (error) {
        console.error("Error refreshing investor:", error);
      }
    }
  };

  // Deposit ETH to contract
  const depositToContract = async (amountEth) => {
    if (!signer || !contractAddress) {
      toast.error("Wallet or contract not connected");
      return null;
    }
    try {
      const tx = await signer.sendTransaction({
        to: contractAddress,
        value: ethers.utils.parseEther(amountEth.toString()),
        data: "0xd0e30db0" // deposit() selector
      });
      toast.info(`Transaction sent: ${tx.hash.slice(0, 10)}...`);
      const receipt = await tx.wait();
      toast.success("Deposit confirmed!");
      await refreshInvestor();
      return receipt;
    } catch (error) {
      console.error("Deposit error:", error);
      toast.error(error.message || "Deposit failed");
      return null;
    }
  };

  return (
    <WalletContext.Provider value={{ 
      wallet, investor, loading, provider, signer, chainId, ethBalance, contractAddress,
      connectWallet, disconnectWallet, refreshInvestor, switchToSepolia, depositToContract 
    }}>
      {children}
    </WalletContext.Provider>
  );
};

export default WalletContext;
