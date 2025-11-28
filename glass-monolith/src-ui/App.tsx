import { useCallback, useMemo, useState } from "react";
import LatticeView from "./components/LatticeView";
import CommandVector from "./components/CommandVector";
import ProofCard, { ProofState } from "./components/ProofCard";

export type TempleStatus = "IDLE" | "PROCESSING" | "VERIFIED" | "ERROR";

export type TempleState = {
  id: string;
  status: TempleStatus;
};

type SystemState = {
  temples: TempleState[];
  proof?: ProofState;
};

const INITIAL_TEMPLES: TempleState[] = [
  "LEX-MON",
  "LEX-VIT",
  "LEX-WTH",
  "LEX-ENT",
  "LEX-ORD",
  "LEX-OPS",
  "LEX-ARC",
  "LEX-SEC",
  "LEX-RES",
  "LEX-TRA",
  "LEX-COM",
  "LEX-INT",
].map((id) => ({ id, status: "IDLE" }));

async function executeVector(command: string): Promise<ProofState> {
  // Best-effort Tauri invoke; fallback to a local mock so the UI works in isolation.
  try {
    const { invoke } = await import("@tauri-apps/api/tauri");
    const result = await invoke<string>("execute_vector", { command });
    return {
      action: command,
      status: result.startsWith("ERROR") ? "REJECTED" : "SIGNED",
      proof: result,
      cost: "$—",
      impact: "Delta resolved",
      signature: "srp://local/mock",
    };
  } catch (err) {
    return {
      action: command,
      status: "SIGNED",
      proof: "STATE UPDATED: DELTA RESOLVED. PROOF: 0xMOCK",
      cost: "$450.00",
      impact: "Runway -2 days",
      signature: "srp://alexis/sigma",
    };
  }
}

export default function App() {
  const [systemState, setSystemState] = useState<SystemState>({
    temples: INITIAL_TEMPLES,
  });

  const [isFiring, setIsFiring] = useState(false);

  const handleCommand = useCallback(async (directive: string) => {
    if (!directive.trim()) return;
    setIsFiring(true);

    // 1) Set processing state on a few deterministic nodes.
    const processingIds = ["LEX-MON", "LEX-VIT", "LEX-WTH"];
    setSystemState((prev) => ({
      ...prev,
      temples: prev.temples.map((t) =>
        processingIds.includes(t.id) ? { ...t, status: "PROCESSING" } : t
      ),
      proof: undefined,
    }));

    // 2) Execute via kernel/bridge.
    const proof = await executeVector(directive);

    // 3) Collapse to convergence (verified) or rejection.
    const converged = proof.status === "SIGNED";
    setSystemState((prev) => ({
      ...prev,
      temples: prev.temples.map((t) => ({
        ...t,
        status: processingIds.includes(t.id)
          ? converged
            ? "VERIFIED"
            : "ERROR"
          : t.status === "PROCESSING"
          ? "IDLE"
          : t.status,
      })),
      proof,
    }));

    setIsFiring(false);
  }, []);

  const headerMetrics = useMemo(
    () => ({
      runway: "132 days",
      bioLoad: "Recovery 87%",
      entropy: "0.00",
    }),
    []
  );

  return (
    <div style={styles.shell}>
      <header style={styles.header}>
        <div style={styles.metric}>
          <span style={styles.label}>Runway</span>
          <span style={styles.value}>{headerMetrics.runway}</span>
        </div>
        <div style={styles.title}>GLASS MONOLITH — LEX-7 CONTROL PLANE</div>
        <div style={styles.metric}>
          <span style={styles.label}>Biometric Load</span>
          <span style={styles.value}>{headerMetrics.bioLoad}</span>
        </div>
        <div style={styles.metric}>
          <span style={styles.label}>Entropy</span>
          <span style={{ ...styles.value, color: "#FF5555" }}>
            {headerMetrics.entropy}
          </span>
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.latticePane}>
          <LatticeView systemState={systemState} />
        </div>
        <div style={styles.sidePane}>
          <CommandVector
            onSubmit={handleCommand}
            isProcessing={isFiring}
            placeholder='Directive: "Authorize deployment of Comet v2."'
          />
          <ProofCard proof={systemState.proof} />
        </div>
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  shell: {
    minHeight: "100vh",
    background: "radial-gradient(circle at 20% 20%, #0c162a 0%, #03060d 45%, #01030a 100%)",
    color: "#F5F7FF",
    fontFamily: "Space Grotesk, 'Sora', 'Inter', system-ui, sans-serif",
    display: "flex",
    flexDirection: "column",
    padding: "16px",
  },
  header: {
    display: "grid",
    gridTemplateColumns: "1fr 2fr 1fr 1fr",
    alignItems: "center",
    gap: "12px",
    padding: "8px 12px",
    border: "1px solid #1b2236",
    background: "rgba(8, 12, 24, 0.8)",
    boxShadow: "0 0 24px rgba(255, 215, 0, 0.05)",
  },
  title: {
    textAlign: "center",
    letterSpacing: "0.12em",
    fontSize: "13px",
    color: "#C1C7D0",
  },
  metric: {
    display: "flex",
    flexDirection: "column",
    gap: "2px",
    fontSize: "12px",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  label: {
    color: "#6F7685",
  },
  value: {
    color: "#F5F7FF",
    fontWeight: 600,
  },
  main: {
    flex: 1,
    display: "grid",
    gridTemplateColumns: "3fr 2fr",
    gap: "16px",
    marginTop: "16px",
  },
  latticePane: {
    border: "1px solid #1b2236",
    background: "rgba(8, 12, 24, 0.65)",
    position: "relative",
  },
  sidePane: {
    display: "grid",
    gridTemplateRows: "auto 1fr",
    gap: "12px",
  },
};
