import React, { useState, useEffect, useRef } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface Directive {
  id: string;
  source: string;
  target: string;
  directive: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  signature: string;
  status: 'pending' | 'routing' | 'delivered' | 'failed';
}

interface DirectiveStreamProps {
  maxItems?: number;
  filter?: string;
}

export const DirectiveStream: React.FC<DirectiveStreamProps> = ({ 
  maxItems = 50,
  filter = 'all'
}) => {
  const [directives, setDirectives] = useState<Directive[]>([]);
  const [realTimeFeed, setRealTimeFeed] = useState<Directive[]>([]);
  const streamRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // Fetch real-time directive stream from Rust backend
        const feed = await invoke<Directive[]>('get_directive_stream');
        setRealTimeFeed(feed);
      } catch (error) {
        console.error('Failed to fetch directive stream:', error);
      }
    }, 500);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Combine initial directives with real-time feed
    const combined = [...realTimeFeed, ...directives];
    // Remove duplicates by ID and limit to maxItems
    const unique = combined.filter((item, index, self) => 
      index === self.findIndex((d) => d.id === item.id)
    ).slice(0, maxItems);
    
    setDirectives(unique);
  }, [realTimeFeed, maxItems]);

  useEffect(() => {
    // Auto-scroll to bottom when new directives arrive
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [directives]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#ff0044';
      case 'high': return '#ff6600';
      case 'medium': return '#ffcc00';
      case 'low': return '#666666';
      default: return '#333333';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'delivered': return '#00ff88';
      case 'routing': return '#ffaa00';
      case 'pending': return '#666666';
      case 'failed': return '#ff0044';
      default: return '#333333';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const filteredDirectives = filter === 'all' 
    ? directives 
    : directives.filter(d => d.priority === filter);

  return (
    <div className="directive-stream glass-panel">
      <div className="stream-header">
        <h3 className="panel-title">BARK PROTOCOL v3.1 STREAM</h3>
        <div className="stream-stats">
          <span className="stat-item">
            Total: {directives.length}
          </span>
          <span className="stat-item">
            Pending: {directives.filter(d => d.status === 'pending').length}
          </span>
          <span className="stat-item">
            Active: {directives.filter(d => d.status === 'routing').length}
          </span>
        </div>
      </div>
      
      <div className="stream-content" ref={streamRef}>
        {filteredDirectives.length === 0 ? (
          <div className="empty-stream">
            <div className="pulse-dot"></div>
            Awaiting directive transmission...
          </div>
        ) : (
          filteredDirectives.map((directive) => (
            <div key={directive.id} className="directive-item">
              <div className="directive-header">
                <div className="directive-id">#{directive.id.slice(-6)}</div>
                <div className="priority-indicator" style={{ backgroundColor: getPriorityColor(directive.priority) }} />
                <div className="status-indicator" style={{ backgroundColor: getStatusColor(directive.status) }} />
                <div className="timestamp">{formatTimestamp(directive.timestamp)}</div>
              </div>
              
              <div className="directive-path">
                <span className="source-node">{directive.source}</span>
                <span className="path-arrow">→</span>
                <span className="target-node">{directive.target}</span>
              </div>
              
              <div className="directive-content">
                <code className="directive-code">{directive.directive}</code>
              </div>
              
              <div className="directive-footer">
                <div className="signature">σ: {directive.signature.slice(0, 16)}...</div>
                <div className="status-text">{directive.status.toUpperCase()}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
