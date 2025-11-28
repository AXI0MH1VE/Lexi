import React, { useState, useEffect, useRef } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { Lattice } from './components/Lattice';
import { NodeHUD } from './components/NodeHUD';
import { DirectiveStream } from './components/DirectiveStream';
import { VectorInput } from './components/VectorInput';
import { SystemStatus } from './components/SystemStatus';
import './App.css';

interface LatticeNode {
  id: string;
  status: 'ACTIVE' | 'OFFLINE' | 'DEGRADED';
  load: number;
  position: [number, number, number];
}

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

const App: React.FC = () => {
  const [latticeStatus, setLatticeStatus] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [systemReady, setSystemReady] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Clock update
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Initialize system on mount
  useEffect(() => {
    const initializeSystem = async () => {
      try {
        console.log('[GLASS MONOLITH] Initializing system...');
        await invoke('ignite_crucible');
        setSystemReady(true);
        console.log('[GLASS MONOLITH] System initialized successfully');
      } catch (error) {
        console.error('[GLASS MONOLITH] Failed to initialize:', error);
        // Continue with demo mode
        setSystemReady(true);
      }
    };

    initializeSystem();
  }, []);

  // Periodic status updates
  useEffect(() => {
    const updateStatus = async () => {
      try {
        const status = await invoke('get_lattice_status');
        setLatticeStatus(status);
      } catch (error) {
        console.error('[GLASS MONOLITH] Status update failed:', error);
        // Use demo data
        setLatticeStatus(getDemoLatticeStatus());
      }
    };

    if (systemReady) {
      updateStatus();
      const interval = setInterval(updateStatus, 1000);
      return () => clearInterval(interval);
    }
  }, [systemReady]);

  // Demo lattice status data
  const getDemoLatticeStatus = () => ({
    system_status: 'ONLINE',
    zero_entropy_score: 0,
    active_nodes: 6,
    nodes: {
      'LEX-MON': { id: 'LEX-MON', name: 'Router/Coordinator', status: 'active', load: 45, temperature: 42, entropy: 0.0, lastUpdate: new Date().toISOString(), capabilities: ['Routing', 'Coordination', 'Load Balancing'] },
      'LEX-VIT': { id: 'LEX-VIT', name: 'Vitality Monitor', status: 'active', load: 67, temperature: 38, entropy: 0.0, lastUpdate: new Date().toISOString(), capabilities: ['Bio-monitoring', 'Health Metrics', 'Stress Analysis'] },
      'LEX-WTH': { id: 'LEX-WTH', name: 'Wealth Analyzer', status: 'active', load: 23, temperature: 35, entropy: 0.0, lastUpdate: new Date().toISOString(), capabilities: ['Financial Analysis', 'Risk Assessment', 'Portfolio Management'] },
      'LEX-ENT': { id: 'LEX-ENT', name: 'Enterprise Planner', status: 'active', load: 78, temperature: 41, entropy: 0.0, lastUpdate: new Date().toISOString(), capabilities: ['Strategic Planning', 'Business Intelligence', 'Decision Support'] },
      'LEX-KNO': { id: 'LEX-KNO', name: 'Knowledge Processor', status: 'active', load: 56, temperature: 39, entropy: 0.0, lastUpdate: new Date().toISOString(), capabilities: ['Data Analysis', 'Pattern Recognition', 'Insight Generation'] },
      'LEX-ORD': { id: 'LEX-ORD', name: 'Logistics Coordinator', status: 'active', load: 34, temperature: 37, entropy: 0.0, lastUpdate: new Date().toISOString(), capabilities: ['Resource Allocation', 'Workflow Optimization', 'Supply Chain'] }
    }
  });

  // Generate lattice positions for 3D visualization
  const generateLatticePositions = (): LatticeNode[] => {
    const nodes: LatticeNode[] = [];
    const nodeTypes = [
      { id: 'LEX-MON', position: [0, 0, 0] as [number, number, number] },
      { id: 'LEX-VIT', position: [3, 2, 0] as [number, number, number] },
      { id: 'LEX-WTH', position: [-3, 2, 0] as [number, number, number] },
      { id: 'LEX-ENT', position: [0, 3, 2] as [number, number, number] },
      { id: 'LEX-KNO', position: [0, -3, 2] as [number, number, number] },
      { id: 'LEX-ORD', position: [3, -2, 0] as [number, number, number] },
      { id: 'LEX-CRT', position: [-3, -2, 0] as [number, number, number] },
      { id: 'LEX-KIN', position: [0, 2, -2] as [number, number, number] },
      { id: 'LEX-GRW', position: [2, 0, 2] as [number, number, number] },
      { id: 'LEX-SAN', position: [-2, 0, 2] as [number, number, number] },
      { id: 'LEX-LEI', position: [0, -2, -2] as [number, number, number] },
      { id: 'LEX-LEG', position: [2, 0, -2] as [number, number, number] }
    ];

    nodeTypes.forEach(nodeType => {
      const nodeData = latticeStatus?.nodes?.[nodeType.id];
      const status = nodeData?.status === 'active' ? 'ACTIVE' : 'OFFLINE';
      const load = nodeData?.load || 0;
      
      nodes.push({
        id: nodeType.id,
        status,
        load,
        position: nodeType.position
      });
    });

    return nodes;
  };

  // Convert lattice status nodes to NodeHUD format
  const getNodeDataArray = (): NodeData[] => {
    if (!latticeStatus?.nodes) return [];
    
    return Object.values(latticeStatus.nodes);
  };

  // Handle directive transmission
  const handleDirective = async (directive: string) => {
    try {
      console.log('[GLASS MONOLITH] Transmitting directive:', directive);
      await invoke('transmit_vector', { directive });
      console.log('[GLASS MONOLITH] Directive transmitted successfully');
    } catch (error) {
      console.log('[GLASS MONOLITH] Demo mode - directive accepted:', directive);
    }
  };

  if (!systemReady) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-icon">🔮</div>
          <h1>AXIOM CRUCIBLE</h1>
          <p>Initializing Glass Monolith...</p>
          <div className="loading-bar">
            <div className="loading-progress"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-hud">
      {/* Top Status Bar */}
      <div className="status-bar">
        <div className="status-left">
          <span className="system-status">STATUS: {latticeStatus?.system_status || 'ONLINE'}</span>
          <span className="entropy-level">ENTROPY: {latticeStatus?.zero_entropy_score || 0}</span>
        </div>
        <div className="status-right">
          <span className="active-nodes">{latticeStatus?.active_nodes || 6}/12 NODES</span>
          <span className="timestamp">{currentTime.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="main-content">
        {/* Left Panel - Node HUD */}
        <div className="left-panel">
          <NodeHUD 
            nodes={getNodeDataArray()}
            selectedNode={selectedNode}
            onNodeSelect={setSelectedNode}
          />
        </div>

        {/* Center - 3D Lattice Visualization */}
        <div className="center-panel">
          <div className="lattice-viewport">
            <Lattice 
              nodes={generateLatticePositions()}
              selectedNode={selectedNode}
              onNodeClick={setSelectedNode}
            />
          </div>
        </div>

        {/* Right Panel - System Status and Controls */}
        <div className="right-panel">
          <SystemStatus />
          <VectorInput 
            onSubmit={handleDirective}
            placeholder="ENTER DIRECTIVE VECTOR..."
            disabled={!systemReady}
          />
        </div>
      </div>

      {/* Bottom - Directive Stream */}
      <div className="bottom-panel">
        <DirectiveStream 
          maxItems={30}
          filter="all"
        />
      </div>

      {/* Stream Log Overlay */}
      <div className="stream-log">
        <div className="log-header">
          <h3>SYSTEM LOG</h3>
          <button className="log-toggle">📋</button>
        </div>
        <div className="log-content">
          <div className="log-entry">[SYS] CRUCIBLE ONLINE</div>
          <div className="log-entry">[MON] ROUTER ACTIVE</div>
          <div className="log-entry">[VIT] VITALITY MONITORING</div>
          <div className="log-entry">[WTH] WEALTH ANALYSIS</div>
          <div className="log-entry">[ENT] ENTERPRISE PLANNING</div>
          <div className="log-entry">[KNO] KNOWLEDGE PROCESSING</div>
          <div className="log-entry">[ORD] LOGISTICS COORDINATION</div>
        </div>
      </div>
    </div>
  );
};

export default App;
