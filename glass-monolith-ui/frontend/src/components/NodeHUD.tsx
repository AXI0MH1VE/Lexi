import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface NodeData {
  id: string;
  name: string;
  status: 'active' | 'standby' | 'error' | 'processing';
  load: number;
  temperature: number;
  entropy: number;
  lastUpdate: string;
  capabilities: string[];
}

interface NodeHUDProps {
  nodes: NodeData[];
  selectedNode: string | null;
  onNodeSelect: (nodeId: string) => void;
}

export const NodeHUD: React.FC<NodeHUDProps> = ({ nodes, selectedNode, onNodeSelect }) => {
  const [realTimeData, setRealTimeData] = useState<Record<string, NodeData>>({});

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // Fetch real-time node data from Rust backend
        const data = await invoke<Record<string, NodeData>>('get_node_status');
        setRealTimeData(data);
      } catch (error) {
        console.error('Failed to fetch node data:', error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#00ff88';
      case 'processing': return '#ffaa00';
      case 'standby': return '#666666';
      case 'error': return '#ff0044';
      default: return '#333333';
    }
  };

  const getLoadBarColor = (load: number) => {
    if (load > 80) return '#ff0044';
    if (load > 60) return '#ffaa00';
    return '#00ff88';
  };

  return (
    <div className="node-hud glass-panel">
      <h3 className="panel-title">LEX NODE MATRIX</h3>
      <div className="node-grid">
        {nodes.map((node) => {
          const realTime = realTimeData[node.id];
          const currentNode = realTime || node;
          
          return (
            <div
              key={node.id}
              className={`node-card ${selectedNode === node.id ? 'selected' : ''}`}
              onClick={() => onNodeSelect(node.id)}
            >
              <div className="node-header">
                <div className="node-id">{currentNode.id}</div>
                <div 
                  className="status-indicator"
                  style={{ backgroundColor: getStatusColor(currentNode.status) }}
                />
              </div>
              
              <div className="node-name">{currentNode.name}</div>
              
              <div className="metrics">
                <div className="metric">
                  <span className="metric-label">LOAD</span>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill"
                      style={{ 
                        width: `${currentNode.load}%`,
                        backgroundColor: getLoadBarColor(currentNode.load)
                      }}
                    />
                  </div>
                  <span className="metric-value">{currentNode.load}%</span>
                </div>
                
                <div className="metric">
                  <span className="metric-label">TEMP</span>
                  <span className="metric-value">{currentNode.temperature}°C</span>
                </div>
                
                <div className="metric">
                  <span className="metric-label">ENTROPY</span>
                  <span className="metric-value">{currentNode.entropy}</span>
                </div>
              </div>
              
              <div className="capabilities">
                {currentNode.capabilities.slice(0, 3).map((cap, idx) => (
                  <span key={idx} className="capability-tag">{cap}</span>
                ))}
                {currentNode.capabilities.length > 3 && (
                  <span className="capability-tag">+{currentNode.capabilities.length - 3}</span>
                )}
              </div>
              
              <div className="last-update">
                Updated: {currentNode.lastUpdate}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
