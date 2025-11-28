import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface SystemMetrics {
  uptime: string;
  totalNodes: number;
  activeNodes: number;
  processingLoad: number;
  memoryUsage: number;
  networkLatency: number;
  entropyLevel: number;
  securityStatus: 'secure' | 'warning' | 'critical';
  lastUpdate: string;
}

interface SystemStatusProps {
  refreshInterval?: number;
}

export const SystemStatus: React.FC<SystemStatusProps> = ({ refreshInterval = 2000 }) => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await invoke<SystemMetrics>('get_system_metrics');
        setMetrics(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch system metrics:', error);
        setIsLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const getSecurityColor = (status: string) => {
    switch (status) {
      case 'secure': return '#00ff88';
      case 'warning': return '#ffaa00';
      case 'critical': return '#ff0044';
      default: return '#666666';
    }
  };

  const formatUptime = (uptime: string) => {
    // Assuming uptime is in seconds
    const seconds = parseInt(uptime);
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    return `${days}d ${hours}h ${minutes}m`;
  };

  if (isLoading) {
    return (
      <div className="system-status glass-panel">
        <h3 className="panel-title">SYSTEM STATUS</h3>
        <div className="loading-state">
          <div className="spinner"></div>
          Initializing Glass Monolith...
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="system-status glass-panel">
        <h3 className="panel-title">SYSTEM STATUS</h3>
        <div className="error-state">
          <div className="error-icon">⚠</div>
          System metrics unavailable
        </div>
      </div>
    );
  }

  return (
    <div className="system-status glass-panel">
      <h3 className="panel-title">AXIOM CRUCIBLE STATUS</h3>
      
      <div className="status-grid">
        <div className="status-item">
          <div className="status-label">UPTIME</div>
          <div className="status-value">{formatUptime(metrics.uptime)}</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">NODE MATRIX</div>
          <div className="status-value">
            <span className="active-count">{metrics.activeNodes}</span>
            <span className="separator">/</span>
            <span className="total-count">{metrics.totalNodes}</span>
          </div>
        </div>
        
        <div className="status-item">
          <div className="status-label">PROCESSING LOAD</div>
          <div className="status-value">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${metrics.processingLoad}%` }}
              />
            </div>
            <span className="percentage">{metrics.processingLoad}%</span>
          </div>
        </div>
        
        <div className="status-item">
          <div className="status-label">MEMORY USAGE</div>
          <div className="status-value">{metrics.memoryUsage}%</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">NETWORK LATENCY</div>
          <div className="status-value">{metrics.networkLatency}ms</div>
        </div>
        
        <div className="status-item">
          <div className="status-label">ENTROPY LEVEL</div>
          <div className="status-value entropy">
            <span className="entropy-value">{metrics.entropyLevel}</span>
            <span className="entropy-badge">ZERO</span>
          </div>
        </div>
        
        <div className="status-item">
          <div className="status-label">SECURITY STATUS</div>
          <div className="status-value security">
            <div 
              className="security-indicator"
              style={{ backgroundColor: getSecurityColor(metrics.securityStatus) }}
            />
            <span className="security-text">{metrics.securityStatus.toUpperCase()}</span>
          </div>
        </div>
        
        <div className="status-item">
          <div className="status-label">LAST UPDATE</div>
          <div className="status-value">{metrics.lastUpdate}</div>
        </div>
      </div>
      
      <div className="system-footer">
        <div className="protocol-info">
          BARK Protocol v3.1 • Ed25519 Cryptography • Mamba-SSM Processing
        </div>
        <div className="version-info">
          Axiom Crucible v1.0 (Glass Monolith)
        </div>
      </div>
    </div>
  );
};
