/**
 * AlphaAI WebSocket Hook
 * Manages real-time signal updates for Pro/Elite users
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';

const WS_BASE_URL = process.env.REACT_APP_BACKEND_URL?.replace('https://', 'wss://').replace('http://', 'ws://');

export const useSignalsWebSocket = () => {
  const { user, isPro, tokens } = useAuth();
  const [signals, setSignals] = useState([]);
  const [prices, setPrices] = useState([]);
  const [connected, setConnected] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const openedAtRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!user || !isPro || !tokens?.access_token) {
      return;
    }

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    const tier = user.is_elite ? 'elite' : 'pro';
    const clientId = `${user.id}:${tier}`;
    const wsUrl = `${WS_BASE_URL}/ws/signals/${clientId}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.debug('[WS Signals] Connected');
        openedAtRef.current = Date.now();
        setConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        
        // Send authentication
        ws.send(JSON.stringify({
          action: 'authenticate',
          token: tokens.access_token
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'connected':
              console.log('WebSocket authenticated:', data.message);
              break;
            
            case 'signals':
              setSignals(data.data || []);
              break;
            
            case 'signal_update':
              // New signal received - prepend to list
              setSignals(prev => {
                const newSignal = data.data;
                const exists = prev.some(s => s.id === newSignal.id);
                if (exists) {
                  return prev.map(s => s.id === newSignal.id ? newSignal : s);
                }
                return [newSignal, ...prev].slice(0, 20);
              });
              
              // Show notification for high-confidence signals
              if (data.data.confidence >= 80) {
                toast.success(
                  `New ${data.data.signal_type} Signal: ${data.data.symbol}`,
                  { description: `Confidence: ${data.data.confidence}%` }
                );
              }
              break;
            
            case 'prices':
              setPrices(data.data || []);
              break;
            
            case 'price_update':
              setPrices(prev => {
                const updated = data.data;
                return prev.map(p => 
                  p.symbol === updated.symbol ? { ...p, ...updated } : p
                );
              });
              break;
            
            case 'subscribed':
              console.log('Subscribed to channel:', data.channel);
              break;
            
            case 'unsubscribed':
              console.log('Unsubscribed from channel:', data.channel);
              break;
            
            case 'pong':
              // Heartbeat response
              break;
            
            case 'error':
              console.error('WebSocket error:', data.message);
              setError(data.message);
              break;
            
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Connection error');
      };

      ws.onclose = (event) => {
        console.debug('[WS Signals] Closed:', event.code, event.reason);
        setConnected(false);
        wsRef.current = null;

        // Don't reconnect if closed intentionally or max attempts reached
        if (event.code === 1000 || reconnectAttemptsRef.current >= maxReconnectAttempts) {
          return;
        }

        // Detect rapid close — increase backoff
        const lifespan = Date.now() - openedAtRef.current;
        const baseDelay = lifespan < 500 ? 5000 : 1000;
        const delay = Math.min(baseDelay * Math.pow(2, reconnectAttemptsRef.current), 30000);
        reconnectAttemptsRef.current++;
        
        console.debug(`[WS Signals] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`);
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      };
    } catch (e) {
      console.error('Failed to create WebSocket:', e);
      setError('Failed to connect');
    }
  }, [user, isPro, tokens]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User initiated disconnect');
      wsRef.current = null;
    }
    
    setConnected(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  const subscribe = useCallback((channel) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe', channel }));
    }
  }, []);

  const unsubscribe = useCallback((channel) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'unsubscribe', channel }));
    }
  }, []);

  const sendPing = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'ping' }));
    }
  }, []);

  // Connect when Pro user is authenticated
  useEffect(() => {
    if (user && isPro) {
      connect();
    } else {
      disconnect();
    }

    return () => disconnect();
  }, [user, isPro, connect, disconnect]);

  // Heartbeat to keep connection alive
  useEffect(() => {
    if (!connected) return;

    const interval = setInterval(sendPing, 30000);
    return () => clearInterval(interval);
  }, [connected, sendPing]);

  return {
    signals,
    prices,
    connected,
    error,
    connect,
    disconnect,
    subscribe,
    unsubscribe
  };
};

export default useSignalsWebSocket;
