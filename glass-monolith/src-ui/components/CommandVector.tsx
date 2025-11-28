import { FormEvent, useState, type CSSProperties } from "react";

type Props = {
  onSubmit: (directive: string) => void;
  isProcessing?: boolean;
  placeholder?: string;
};

export default function CommandVector({ onSubmit, isProcessing = false, placeholder }: Props) {
  const [text, setText] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit(text.trim());
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} style={styles.frame}>
      <div style={styles.label}>Command Vector</div>
      <div style={styles.row}>
        <span style={styles.prompt}>≫</span>
        <input
          style={styles.input}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          disabled={isProcessing}
        />
        <button style={styles.button} type="submit" disabled={isProcessing}>
          {isProcessing ? "Resolving" : "Fire"}
        </button>
      </div>
      <div style={styles.hint}>
        Press CMD/CTRL+K to focus. System enforces Zero Entropy (signed directives only).
      </div>
    </form>
  );
}

const styles: Record<string, CSSProperties> = {
  frame: {
    border: "1px solid #1b2236",
    background: "rgba(8, 12, 24, 0.8)",
    padding: "12px 14px",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "12px",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: "#7B8497",
  },
  row: {
    display: "grid",
    gridTemplateColumns: "24px 1fr 96px",
    alignItems: "center",
    gap: "10px",
  },
  prompt: {
    color: "#FFD700",
    fontWeight: 700,
    fontSize: "16px",
    textAlign: "center",
  },
  input: {
    background: "rgba(15, 21, 36, 0.9)",
    color: "#F5F7FF",
    border: "1px solid #1f2840",
    padding: "10px 12px",
    borderRadius: "4px",
    fontSize: "15px",
  },
  button: {
    height: "38px",
    background: "linear-gradient(135deg, #FFD700, #FF9B00)",
    color: "#0b0f1a",
    border: "none",
    borderRadius: "4px",
    fontWeight: 700,
    letterSpacing: "0.06em",
    cursor: "pointer",
  },
  hint: {
    fontSize: "11px",
    color: "#5E6780",
  },
};
