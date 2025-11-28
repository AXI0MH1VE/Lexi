import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Suspense, useMemo, useRef, type CSSProperties } from "react";
import type { TempleState } from "../App";

type Props = {
  systemState: {
    temples: TempleState[];
  };
};

function TempleNode({ id, status, position }: TempleState & { position: [number, number, number] }) {
  const mesh = useRef<THREE.Mesh>(null);
  const color =
    status === "VERIFIED" ? "#FFD700" : status === "ERROR" ? "#FF3B30" : status === "PROCESSING" ? "#2FA4FF" : "#112233";

  useFrame(() => {
    if (!mesh.current) return;
    if (status === "PROCESSING") {
      mesh.current.rotation.x += 0.04;
      mesh.current.rotation.y += 0.02;
    }
  });

  return (
    <mesh ref={mesh} position={position}>
      <dodecahedronGeometry args={[0.9, 0]} />
      <meshStandardMaterial color={color} wireframe emissive={color} emissiveIntensity={2} />
    </mesh>
  );
}

export default function LatticeView({ systemState }: Props) {
  const positions = useMemo(
    () =>
      systemState.temples.map((_, i) => {
        const radius = 5;
        const angle = (i / systemState.temples.length) * Math.PI * 2;
        return [Math.cos(angle) * radius, Math.sin(angle) * radius, 0] as [number, number, number];
      }),
    [systemState.temples.length]
  );

  return (
    <div style={containerStyle}>
      <Canvas camera={{ position: [0, 0, 14], fov: 45 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[0, 0, 10]} intensity={1.2} color="#FFD700" />
        <Suspense fallback={null}>
          {systemState.temples.map((t, idx) => (
            <TempleNode key={t.id} {...t} position={positions[idx]} />
          ))}
        </Suspense>
        <gridHelper args={[16, 8, "#112244", "#11131f"]} />
      </Canvas>
    </div>
  );
}

const containerStyle: CSSProperties = {
  width: "100%",
  height: "100%",
  minHeight: "420px",
  background: "radial-gradient(circle at 50% 50%, rgba(255,255,255,0.04), rgba(0,0,0,0.45))",
  borderBottom: "1px solid #1b2236",
};
