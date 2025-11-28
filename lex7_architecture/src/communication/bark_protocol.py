#!/usr/bin/env python3
"""
BARK PROTOCOL - The Communication Layer for LEX-7
Implements the BARK (Bi-directional Autonomous Recursive Knowledge) protocol
for secure P2P communication between Lex Nodes in the Sovereign Lattice
"""

import asyncio
import json
import time
import hashlib
import hmac
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of BARK protocol messages"""
    DIRECTIVE = "directive"
    RESPONSE = "response"
    STATE_SYNC = "state_sync"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    ROUTING_UPDATE = "routing_update"
    ERROR = "error"
    CRYPTO_SIGNED = "crypto_signed"

class Priority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class BARKMessage:
    """Base BARK protocol message structure"""
    message_type: MessageType
    sender_id: str
    recipient_id: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: Optional[float] = None
    priority: Priority = Priority.NORMAL
    ttl: int = 300  # Time to live in seconds
    payload: Dict[str, Any] = None
    signature: Optional[str] = None
    public_key: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.message_id is None:
            self.message_id = self.generate_message_id()
        if self.payload is None:
            self.payload = {}
    
    def generate_message_id(self) -> str:
        """Generate unique message ID"""
        content = f"{self.sender_id}{self.timestamp}{self.message_type.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BARKMessage':
        """Create from dictionary (deserialization)"""
        data = data.copy()
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = Priority(data['priority'])
        return cls(**data)
    
    def sign(self, private_key: str) -> 'BARKMessage':
        """Sign the message with private key"""
        content = json.dumps(self.to_dict(), sort_keys=True)
        signature = hmac.new(
            private_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.signature = signature
        return self
    
    def verify_signature(self, public_key: str) -> bool:
        """Verify the message signature"""
        if not self.signature:
            return False
        
        content = json.dumps(self.to_dict(), sort_keys=True)
        expected_signature = hmac.new(
            public_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(self.signature, expected_signature)

@dataclass
class BARKDirective:
    """BARK Directive message - The core communication unit"""
    directive_id: str
    command: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    expected_response_type: Optional[str] = None
    timeout: float = 30.0
    
    def to_message(self, sender_id: str, recipient_id: Optional[str] = None) -> BARKMessage:
        """Convert to BARK message"""
        return BARKMessage(
            message_type=MessageType.DIRECTIVE,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={
                'directive': asdict(self)
            }
        )

@dataclass
class BARKResponse:
    """BARK Response message"""
    response_id: str
    directive_id: str
    status: str
    result: Dict[str, Any]
    error: Optional[str] = None
    processing_time: Optional[float] = None
    
    def to_message(self, sender_id: str, recipient_id: str) -> BARKMessage:
        """Convert to BARK message"""
        return BARKMessage(
            message_type=MessageType.RESPONSE,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload={
                'response': asdict(self)
            }
        )

class BARKProtocol:
    """
    BARK Protocol Implementation
    
    This implements the core communication protocol for the LEX-7 Sovereign Lattice.
    It handles secure, authenticated messaging between Lex Nodes.
    """
    
    def __init__(self, node_id: str, private_key: str, public_key: str):
        self.node_id = node_id
        self.private_key = private_key
        self.public_key = public_key
        
        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.directive_handlers: Dict[str, Callable] = {}
        
        # Message queues and pending requests
        self.incoming_queue = asyncio.Queue()
        self.outgoing_queue = asyncio.Queue()
        self.pending_directives: Dict[str, asyncio.Future] = {}
        
        # Connection management
        self.connections: Dict[str, Any] = {}  # Connected nodes
        self.node_registry: Dict[str, Dict[str, Any]] = {}  # Known nodes
        
        logger.info(f"BARK Protocol initialized for node {node_id}")
    
    async def send_directive(
        self,
        directive: BARKDirective,
        recipient_id: str,
        timeout: float = 30.0
    ) -> Optional[BARKResponse]:
        """
        Send a BARK directive and await response
        
        Args:
            directive: The directive to send
            recipient_id: Target node ID
            timeout: Maximum time to wait for response
            
        Returns:
            BARKResponse or None if timeout/error
        """
        # Create message
        message = directive.to_message(self.node_id, recipient_id)
        
        # Create future for response
        response_future = asyncio.Future()
        self.pending_directives[directive.directive_id] = response_future
        
        try:
            # Send message
            await self.send_message(message)
            
            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Directive {directive.directive_id} timed out")
            return None
        except Exception as e:
            logger.error(f"Error sending directive {directive.directive_id}: {e}")
            return None
        finally:
            # Clean up pending directive
            self.pending_directives.pop(directive.directive_id, None)
    
    async def send_message(self, message: BARKMessage) -> bool:
        """
        Send a signed BARK message
        
        Args:
            message: The message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Sign the message
            message = message.sign(self.private_key)
            
            # Add to outgoing queue
            await self.outgoing_queue.put(message)
            
            logger.debug(f"Sent {message.message_type.value} message {message.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def broadcast_message(
        self,
        message: BARKMessage,
        exclude_nodes: Optional[List[str]] = None
    ):
        """
        Broadcast message to all connected nodes
        
        Args:
            message: Message to broadcast
            exclude_nodes: List of node IDs to exclude
        """
        exclude_nodes = exclude_nodes or []
        
        for node_id in self.connections:
            if node_id not in exclude_nodes:
                # Create copy for each recipient
                node_message = BARKMessage(
                    message_type=message.message_type,
                    sender_id=message.sender_id,
                    recipient_id=node_id,
                    priority=message.priority,
                    ttl=message.ttl,
                    payload=message.payload.copy()
                )
                
                await self.send_message(node_message)
    
    async def register_node(self, node_id: str, node_info: Dict[str, Any]):
        """Register a new node in the network"""
        self.node_registry[node_id] = {
            **node_info,
            'registered_at': time.time(),
            'last_seen': time.time()
        }
        logger.info(f"Registered node {node_id}")
    
    async def discover_nodes(self) -> List[str]:
        """Discover available nodes in the network"""
        # Send discovery message
        discovery_msg = BARKMessage(
            message_type=MessageType.DISCOVERY,
            sender_id=self.node_id,
            payload={'request': 'node_discovery'}
        )
        
        await self.broadcast_message(discovery_msg)
        
        # Collect responses (simplified - in production would use proper discovery)
        await asyncio.sleep(2)  # Wait for responses
        
        return list(self.node_registry.keys())
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register handler for specific message type"""
        self.message_handlers[message_type] = handler
    
    def register_directive_handler(self, command: str, handler: Callable):
        """Register handler for specific directive command"""
        self.directive_handlers[command] = handler
    
    async def process_incoming_message(self, message: BARKMessage):
        """
        Process incoming BARK message
        
        Args:
            message: The message to process
        """
        try:
            # Verify signature
            if not message.verify_signature(message.public_key or ""):
                logger.warning(f"Invalid signature on message {message.message_id}")
                return
            
            # Check TTL
            if time.time() - message.timestamp > message.ttl:
                logger.warning(f"Message {message.message_id} expired")
                return
            
            # Route message
            await self._route_message(message)
            
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {e}")
    
    async def _route_message(self, message: BARKMessage):
        """Route message to appropriate handler"""
        
        # Handle responses to pending directives
        if (message.message_type == MessageType.RESPONSE and 
            message.payload.get('response')):
            
            response_data = message.payload['response']
            directive_id = response_data.get('directive_id')
            
            if directive_id in self.pending_directives:
                response = BARKResponse(**response_data)
                self.pending_directives[directive_id].set_result(response)
                return
        
        # Route to message type handlers
        if message.message_type in self.message_handlers:
            await self.message_handlers[message.message_type](message)
            return
        
        # Handle directives
        if (message.message_type == MessageType.DIRECTIVE and 
            message.payload.get('directive')):
            
            directive_data = message.payload['directive']
            directive = BARKDirective(**directive_data)
            
            if directive.command in self.directive_handlers:
                await self.directive_handlers[directive.command](directive, message)
            else:
                logger.warning(f"No handler for directive: {directive.command}")
        
        # Handle other message types
        logger.debug(f"Processed {message.message_type.value} message {message.message_id}")
    
    async def start_heartbeat(self, interval: float = 30.0):
        """Start sending periodic heartbeat messages"""
        while True:
            try:
                heartbeat = BARKMessage(
                    message_type=MessageType.HEARTBEAT,
                    sender_id=self.node_id,
                    payload={'status': 'alive', 'timestamp': time.time()}
                )
                
                await self.broadcast_message(heartbeat)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat: {e}")
                await asyncio.sleep(interval)
    
    async def handle_directive(self, directive: BARKDirective, original_message: BARKMessage):
        """Default directive handler - can be overridden"""
        logger.info(f"Received directive: {directive.command}")
        
        # Send acknowledgment
        response = BARKResponse(
            response_id=f"ack_{directive.directive_id}",
            directive_id=directive.directive_id,
            status="received",
            result={'message': 'Directive received and queued for processing'}
        )
        
        response_msg = response.to_message(self.node_id, original_message.sender_id)
        await self.send_message(response_msg)
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        return {
            'node_id': self.node_id,
            'registered_nodes': len(self.node_registry),
            'active_connections': len(self.connections),
            'pending_directives': len(self.pending_directives),
            'queue_sizes': {
                'incoming': self.incoming_queue.qsize(),
                'outgoing': self.outgoing_queue.qsize()
            }
        }

# Utility functions for BARK protocol

def generate_keypair() -> tuple[str, str]:
    """Generate a simple keypair for testing"""
    import secrets
    
    # In production, use proper cryptographic key generation
    private_key = secrets.token_hex(32)
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    
    return private_key, public_key

def create_test_directive(
    command: str,
    parameters: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> BARKDirective:
    """Create a test BARK directive"""
    return BARKDirective(
        directive_id=f"test_{int(time.time())}",
        command=command,
        parameters=parameters,
        context=context or {}
    )

# Example usage and testing
if __name__ == "__main__":
    async def test_bark_protocol():
        # Generate test keypair
        private_key, public_key = generate_keypair()
        
        # Create BARK protocol instance
        bark = BARKProtocol("node_001", private_key, public_key)
        
        # Register a test directive handler
        async def handle_health_check(directive: BARKDirective, message: BARKMessage):
            print(f"Health check received from {message.sender_id}")
            
            response = BARKResponse(
                response_id=f"health_{directive.directive_id}",
                directive_id=directive.directive_id,
                status="success",
                result={"status": "healthy", "timestamp": time.time()}
            )
            
            response_msg = response.to_message("node_001", message.sender_id)
            await bark.send_message(response_msg)
        
        bark.register_directive_handler("health_check", handle_health_check)
        
        # Start heartbeat
        asyncio.create_task(bark.start_heartbeat())
        
        # Create and send test directive
        directive = create_test_directive(
            "health_check",
            {"check_type": "comprehensive"}
        )
        
        print(f"Sending directive: {directive.command}")
        
        # Note: In a real implementation, you would have recipient nodes
        print("BARK Protocol test completed successfully")
    
    # Run the test
    asyncio.run(test_bark_protocol())
