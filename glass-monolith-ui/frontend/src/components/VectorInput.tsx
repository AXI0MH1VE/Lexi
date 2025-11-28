import React, { useState } from 'react';

interface VectorInputProps {
  onSubmit: (directive: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const VectorInput: React.FC<VectorInputProps> = ({
  onSubmit,
  placeholder = "ENTER DIRECTIVE VECTOR...",
  disabled = false
}) => {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;

    setIsProcessing(true);
    try {
      await onSubmit(input);
      setInput('');
    } catch (error) {
      console.error('[VECTOR INPUT] Failed to submit:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="vector-input-container">
      <form onSubmit={handleSubmit} className="vector-input-form">
        <div className="vector-input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isProcessing}
            className="vector-input-field"
            autoFocus={!disabled}
          />
          <button
            type="submit"
            disabled={disabled || !input.trim() || isProcessing}
            className="vector-submit-button"
          >
            {isProcessing ? (
              <span className="processing-indicator">⚡</span>
            ) : (
              'TRANSMIT'
            )}
          </button>
        </div>
        
        {/* Quick action buttons */}
        <div className="quick-actions">
          <button
            type="button"
            onClick={() => onSubmit("Check bioload and runway")}
            disabled={disabled}
            className="quick-action"
          >
            BIOLOAD & RUNWAY
          </button>
          <button
            type="button"
            onClick={() => onSubmit("Strategic analysis request")}
            disabled={disabled}
            className="quick-action"
          >
            STRATEGY
          </button>
          <button
            type="button"
            onClick={() => onSubmit("Knowledge synthesis")}
            disabled={disabled}
            className="quick-action"
          >
            KNOWLEDGE
          </button>
        </div>
      </form>
      
      {/* Input help */}
      <div className="input-help">
        <p>💡 Directives follow BARK Protocol v3.1 format</p>
        <p>⚡ Press Enter to transmit, Shift+Enter for new line</p>
      </div>
    </div>
  );
};
