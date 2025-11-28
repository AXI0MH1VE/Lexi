import React, { useState, useEffect, useRef } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
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

const App: React.FC = () => {
  const [latticeStatus, setLatticeStatus] = useState<any>(null);
  const [activeDirectives, setActiveDirectives] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [systemReady, setSystemReady] = useState(false);

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
        
        const directives = await invoke('get_active_directives');
        setActiveDirectives(directives as any[]);
      } catch (error) {
        console.error('[GLASS MONOLITH] Status update failed:', error);
      }
    };

    if (systemReady) {
      updateStatus();
      const interval = setInterval(updateStatus, 1000);
      return () => clearInterval(interval);
    }
  }, [systemReady]);

  // Handle directive transmission
  const handleDirective = async (directive: string) => {
    try {
      console.log('[GLASS MONOLITH] Transmitting directive:', directive);
      const response = await invoke('transmit_vector', { directive });
      console.log('[GLASS MONOLITH] Directive response:', response);
      
      // Update active directives
      const directives = await invoke('get_active_directives');
      setActiveDirectives(directives as any[]);
    } catch (error) {
      console.error('[GLASS MONOLITH] Directive transmission failed:', error);
    }
  };

  // Generate lattice positions
  const generateLatticePositions = (): LatticeNode[] => {
    if (!latticeStatus?.nodes) return [];
    
    const nodes: LatticeNode[] = [];
    const nodeTypes = [
      { id: 'LEX-MON', position: [0, 0, 0] as [number, number, number], color: '#FFD700' },
      { id: 'LEX-VIT', position: [3, 2, 0] as [number, number, number], color: '#FF6B6B' },
      { id: 'LEX-WTH', position: [-3, 2, 0] as [number, number, number], color: '#4ECDC4' },
      { id: 'LEX-ENT', position: [0, 3, 2] as [number, number, number], color: '#45B7D1' },
      { id: 'LEX-KNO', position: [0, -3, 2] as [number, number, number], color: '#96CEB4' },
      { id: 'LEX-ORD', position: [3, -2, 0] as [number, number, number], color: '#FFEAA7' },
      { id: 'LEX-CRT', position: [-3, -2, 0] as [number, number, number], color: '#DDA0DD' },
      { id: 'LEX-KIN', position: [0, 2, -2] as [number, number, number], color: '#98D8C8' },
      { id: 'LEX-GRW', position: [2, 0, 2] as [number, number, number], color: '#F7DC6F' },
      { id: 'LEX-SAN', position: [-2, 0, 2] as [number, number, number], color: '#BB8FCE' },
      { id: 'LEX-LEI', position: [0, -2, -2] as [number, number, number], color: '#85C1E9' },
      { id: 'LEX-LEG', position: [2, 0, -2] as [number, number, number], color: '#F8C471' }
    ];

    nodeTypes.forEach(nodeType => {
      const status = latticeStatus.nodes[nodeType.id]?.status || 'OFFLINE';
      const load = latticeStatus.nodes[nodeType.id]?.load || 0;
      
      nodes.push({
        id: nodeType.id,
        status,
        load,
        position: nodeType.position
      });
    });

    return nodes;
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
      {/* System Status Bar */}
      <div className="status-bar">
        <div className="status-left">
          <span className="system-status">STATUS: {latticeStatus?.system_status || 'OFFLINE'}</span>
          <span className="entropy-level">ENTROPY: {latticeStatus?.zero_entropy_score || 0}</span>
        </div>
        <div className="status-right">
          <span className="active-nodes">{latticeStatus?.active_nodes || 0}/12 NODES</span>
          <span className="timestamp">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* 3D Lattice Visualization */}
      <div className="lattice-viewport">
        <Canvas camera={{ position: [10, 10, 10], fov: 75 }}>
          <ambientLight intensity={0.3} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <Lattice 
            nodes={generateLatticePositions()}
            selectedNode={selectedNode}
            onNodeClick={setSelectedNode}
          />
          <OrbitControls 
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            maxDistance={50}
            minDistance={5}
          />
        </Canvas>
      </div>

      {/* Node HUD */}
      {selectedNode && latticeStatus?.nodes && (
        <NodeHUD 
          node={latticeStatus.nodes[selectedNode]}
          nodeId={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}

      {/* Directive Stream */}
      <DirectiveStream 
        directives={activeDirectives}
        onDirectiveSelect={(directive) => console.log('Selected directive:', directive)}
      />

      {/* Vector Input Interface */}
      <VectorInput 
        onSubmit={handleDirective}
        placeholder="ENTER DIRECTIVE VECTOR..."
        disabled={!systemReady}
      />

      {/* System Status Panel */}
      <SystemStatus 
        status={latticeStatus}
        onRefresh={() => window.location.reload()}
      />

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
        </div>
      </div>
    </div>
  );
};

export default App;
