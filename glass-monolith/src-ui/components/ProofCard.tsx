import type { CSSProperties } from "react";

export type ProofState = {
  action: string;
  status: "SIGNED" | "REJECTED";
  proof: string;
  cost?: string;
  impact?: string;
  signature?: string;
};

type Props = {
  proof?: ProofState;
};

export default function ProofCard({ proof }: Props) {
  if (!proof) {
    return (
      <div style={styles.frame}>
        <div style={styles.header}>Proof Card</div>
        <div style={styles.placeholder}>Awaiting convergence...</div>
      </div>
    );
  }

  const accent = proof.status === "SIGNED" ? "#FFD700" : "#FF3B30";

  return (
    <div style={{ ...styles.frame, borderColor: accent }}>
      <div style={styles.header}>Proof Card</div>
      <div style={{ ...styles.badge, color: "#0b0f1a", background: accent }}>{proof.status}</div>
      <div style={styles.item}>
        <span style={styles.label}>Action</span>
        <span style={styles.value}>{proof.action}</span>
      </div>
      <div style={styles.item}>
        <span style={styles.label}>Cost</span>
        <span style={styles.value}>{proof.cost ?? "—"}</span>
      </div>
      <div style={styles.item}>
        <span style={styles.label}>Impact</span>
        <span style={styles.value}>{proof.impact ?? "—"}</span>
      </div>
      <div style={styles.item}>
        <span style={styles.label}>Signature</span>
        <span style={styles.value}>{proof.signature ?? "—"}</span>
      </div>
      <div style={styles.proofBox}>{proof.proof}</div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  frame: {
    border: "1px solid #1b2236",
    background: "rgba(8, 12, 24, 0.9)",
    padding: "12px 14px",
    display: "grid",
    gap: "8px",
    alignContent: "start",
    minHeight: "200px",
  },
  header: {
    fontSize: "12px",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: "#7B8497",
  },
  badge: {
    padding: "6px 10px",
    borderRadius: "4px",
    width: "fit-content",
    fontWeight: 700,
    letterSpacing: "0.08em",
    fontSize: "12px",
  },
  item: {
    display: "flex",
    justifyContent: "space-between",
    gap: "12px",
    fontSize: "13px",
  },
  label: {
    color: "#6F7685",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
  },
  value: {
    color: "#F5F7FF",
    fontWeight: 600,
  },
  proofBox: {
    border: "1px solid #1f2840",
    padding: "10px",
    borderRadius: "4px",
    background: "rgba(15, 21, 36, 0.6)",
    color: "#C1C7D0",
    fontSize: "12px",
    lineHeight: 1.4,
  },
  placeholder: {
    color: "#4E5568",
    fontSize: "13px",
  },
};
