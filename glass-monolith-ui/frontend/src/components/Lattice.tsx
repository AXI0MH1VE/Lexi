import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Text } from '@react-three/drei';
import * as THREE from 'three';

interface LatticeNode {
  id: string;
  status: 'ACTIVE' | 'OFFLINE' | 'DEGRADED';
  load: number;
  position: [number, number, number];
}

interface LatticeProps {
  nodes: LatticeNode[];
  selectedNode: string | null;
  onNodeClick: (nodeId: string) => void;
}

// Animated node component
const LatticeNode: React.FC<{
  node: LatticeNode;
  isSelected: boolean;
  onClick: () => void;
}> = ({ node, isSelected, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state, delta) => {
    if (meshRef.current) {
      // Pulsing animation based on node load
      const pulse = Math.sin(state.clock.elapsedTime * 2 + node.load * 5) * 0.1;
      meshRef.current.scale.setScalar(1 + pulse);
      
      // Rotation for active nodes
      if (node.status === 'ACTIVE') {
        meshRef.current.rotation.y += delta * 0.5;
      }
    }
  });

  const getNodeColor = (status: string, load: number) => {
    switch (status) {
      case 'ACTIVE':
        const intensity = Math.max(0.3, 1 - load * 0.5);
        return new THREE.Color(intensity, intensity * 0.8, intensity * 1.2);
      case 'DEGRADED':
        return new THREE.Color(1, 0.5, 0); // Orange
      case 'OFFLINE':
      default:
        return new THREE.Color(0.3, 0.3, 0.3); // Gray
    }
  };

  const getNodeSize = (status: string, load: number) => {
    const baseSize = status === 'ACTIVE' ? 0.8 : 0.5;
    return baseSize + load * 0.3;
  };

  return (
    <group position={node.position}>
      <Sphere
        ref={meshRef}
        args={[getNodeSize(node.status, node.load), 32, 32]}
        onClick={onClick}
      >
        <meshPhongMaterial
          color={getNodeColor(node.status, node.load)}
          transparent
          opacity={isSelected ? 1.0 : 0.8}
          emissive={node.status === 'ACTIVE' ? getNodeColor(node.status, node.load) : new THREE.Color(0, 0, 0)}
          emissiveIntensity={node.status === 'ACTIVE' ? 0.2 : 0}
        />
      </Sphere>
      
      {/* Node Label */}
      <Text
        position={[0, getNodeSize(node.status, node.load) + 0.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {node.id}
      </Text>
      
      {/* Load indicator */}
      <Text
        position={[0, getNodeSize(node.status, node.load) + 0.1, 0]}
        fontSize={0.2}
        color="#CCCCCC"
        anchorX="center"
        anchorY="middle"
      >
        {(node.load * 100).toFixed(0)}%
      </Text>
      
      {/* Selection ring */}
      {isSelected && (
        <Sphere
          args={[getNodeSize(node.status, node.load) + 0.2, 32, 32]}
        >
          <meshBasicMaterial
            color="#FFD700"
            transparent
            opacity={0.3}
            side={THREE.BackSide}
          />
        </Sphere>
      )}
    </group>
  );
};

// Connection lines between nodes
const LatticeConnections: React.FC<{ nodes: LatticeNode[] }> = ({ nodes }) => {
  const lines = [];
  
  // Central router (LEX-MON) connects to all other nodes
  const routerNode = nodes.find(n => n.id === 'LEX-MON');
  if (routerNode) {
    nodes.forEach(node => {
      if (node.id !== 'LEX-MON') {
        const points = [
          new THREE.Vector3(...routerNode.position),
          new THREE.Vector3(...node.position)
        ];
        
        lines.push(
          <line key={`connection-${routerNode.id}-${node.id}`}>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={2}
                array={new Float32Array([
                  ...routerNode.position,
                  ...node.position
                ])}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial
              color={node.status === 'ACTIVE' ? "#00FFFF" : "#444444"}
              transparent
              opacity={node.status === 'ACTIVE' ? 0.6 : 0.2}
            />
          </line>
        );
      }
    });
  }
  
  return <group>{lines}</group>;
};

export const Lattice: React.FC<LatticeProps> = ({ nodes, selectedNode, onNodeClick }) => {
  return (
    <group>
      {/* Node connections */}
      <LatticeConnections nodes={nodes} />
      
      {/* Individual nodes */}
      {nodes.map(node => (
        <LatticeNode
          key={node.id}
          node={node}
          isSelected={selectedNode === node.id}
          onClick={() => onNodeClick(node.id)}
        />
      ))}
      
      {/* Ambient lighting for the lattice */}
      <pointLight position={[0, 0, 0]} intensity={0.5} color="#FFD700" />
      
      {/* Grid helper for reference */}
      <gridHelper args={[20, 20, "#444444", "#222222"]} position={[0, -5, 0]} />
    </group>
  );
};
