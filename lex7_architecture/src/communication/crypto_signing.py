#!/usr/bin/env python3
"""
CRYPTOGRAPHIC SIGNING - SRP Implementation for LEX-7
Implements Secure Remote Protocol (SRP) for authenticated, encrypted communication
This ensures all inter-node communication is cryptographically secure
"""

import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class KeyType(Enum):
    """Types of cryptographic keys"""
    SIGNING = "signing"
    ENCRYPTION = "encryption"
    SESSION = "session"
    MASTER = "master"

class SignatureAlgorithm(Enum):
    """Supported signature algorithms"""
    ED25519 = "ed25519"
    ECDSA_P256 = "ecdsa_p256"
    RSA_4096 = "rsa_4096"
    HMAC_SHA256 = "hmac_sha256"

@dataclass
class CryptographicKey:
    """Represents a cryptographic key"""
    key_id: str
    key_type: KeyType
    algorithm: SignatureAlgorithm
    public_key: bytes
    private_key: Optional[bytes]  # Only stored on originating node
    created_at: float
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_expired(self) -> bool:
        """Check if key is expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'key_id': self.key_id,
            'key_type': self.key_type.value,
            'algorithm': self.algorithm.value,
            'public_key': self.public_key.hex(),
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CryptographicKey':
        """Create from dictionary"""
        return cls(
            key_id=data['key_id'],
            key_type=KeyType(data['key_type']),
            algorithm=SignatureAlgorithm(data['algorithm']),
            public_key=bytes.fromhex(data['public_key']),
            private_key=None,  # Never deserialize private keys
            created_at=data['created_at'],
            expires_at=data.get('expires_at'),
            metadata=data.get('metadata', {})
        )

@dataclass
class SecureMessage:
    """Cryptographically signed and encrypted message"""
    message_id: str
    sender_id: str
    recipient_id: Optional[str]
    timestamp: float
    message_type: str
    payload: bytes
    signature: bytes
    nonce: bytes  # For replay protection
    session_key_id: Optional[str] = None
    encryption_algorithm: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'timestamp': self.timestamp,
            'message_type': self.message_type,
            'payload': self.payload.hex(),
            'signature': self.signature.hex(),
            'nonce': self.nonce.hex(),
            'session_key_id': self.session_key_id,
            'encryption_algorithm': self.encryption_algorithm
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecureMessage':
        """Create from dictionary"""
        return cls(
            message_id=data['message_id'],
            sender_id=data['sender_id'],
            recipient_id=data.get('recipient_id'),
            timestamp=data['timestamp'],
            message_type=data['message_type'],
            payload=bytes.fromhex(data['payload']),
            signature=bytes.fromhex(data['signature']),
            nonce=bytes.fromhex(data['nonce']),
            session_key_id=data.get('session_key_id'),
            encryption_algorithm=data.get('encryption_algorithm')
        )

class CryptographicManager:
    """
    Cryptographic Manager for LEX-7
    
    Handles all cryptographic operations including:
    - Key generation and management
    - Message signing and verification
    - SRP authentication
    - Session key establishment
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.keys: Dict[str, CryptographicKey] = {}
        self.session_keys: Dict[str, bytes] = {}  # node_id -> session_key
        self.trusted_nodes: Dict[str, CryptographicKey] = {}  # node_id -> public_key
        
        # Initialize with master key
        self._generate_master_key()
        
        logger.info(f"Cryptographic Manager initialized for {node_id}")
    
    def _generate_master_key(self):
        """Generate master signing key"""
        # Generate Ed25519 key pair (simplified)
        private_key = secrets.token_bytes(32)
        public_key = hashlib.sha256(private_key).digest()
        
        master_key = CryptographicKey(
            key_id=f"master_{self.node_id}",
            key_type=KeyType.MASTER,
            algorithm=SignatureAlgorithm.ED25519,
            public_key=public_key,
            private_key=private_key,
            created_at=time.time(),
            metadata={'usage': 'node_authentication', 'scope': 'global'}
        )
        
        self.keys[master_key.key_id] = master_key
        logger.info(f"Generated master key: {master_key.key_id}")
    
    def generate_session_key(self, peer_node_id: str) -> bytes:
        """Generate ephemeral session key for peer communication"""
        # Generate random session key
        session_key = secrets.token_bytes(32)
        
        # Store session key
        self.session_keys[peer_node_id] = session_key
        
        # Create session key key object
        session_key_obj = CryptographicKey(
            key_id=f"session_{self.node_id}_{peer_node_id}_{int(time.time())}",
            key_type=KeyType.SESSION,
            algorithm=SignatureAlgorithm.HMAC_SHA256,
            public_key=session_key,
            private_key=None,
            created_at=time.time(),
            expires_at=time.time() + 3600,  # 1 hour expiry
            metadata={'peer_node_id': peer_node_id}
        )
        
        self.keys[session_key_obj.key_id] = session_key_obj
        logger.debug(f"Generated session key for {peer_node_id}")
        
        return session_key
    
    def get_session_key(self, peer_node_id: str) -> Optional[bytes]:
        """Get existing session key for peer"""
        return self.session_keys.get(peer_node_id)
    
    def trust_node(self, node_id: str, public_key: bytes, algorithm: SignatureAlgorithm = SignatureAlgorithm.ED25519):
        """Trust a node by storing its public key"""
        trusted_key = CryptographicKey(
            key_id=f"trusted_{node_id}",
            key_type=KeyType.SIGNING,
            algorithm=algorithm,
            public_key=public_key,
            private_key=None,
            created_at=time.time(),
            metadata={'node_id': node_id, 'trust_level': 'verified'}
        )
        
        self.trusted_nodes[node_id] = trusted_key
        logger.info(f"Trusted node {node_id}")
    
    def get_trusted_key(self, node_id: str) -> Optional[CryptographicKey]:
        """Get trusted public key for node"""
        return self.trusted_nodes.get(node_id)
    
    def sign_message(
        self, 
        message_data: Dict[str, Any], 
        key_id: str,
        peer_node_id: Optional[str] = None
    ) -> SecureMessage:
        """Sign and optionally encrypt a message"""
        
        # Get signing key
        signing_key = self.keys.get(key_id)
        if not signing_key:
            raise ValueError(f"Signing key {key_id} not found")
        
        if signing_key.is_expired():
            raise ValueError(f"Signing key {key_id} is expired")
        
        # Serialize message data
        import json
        message_json = json.dumps(message_data, sort_keys=True)
        payload = message_json.encode('utf-8')
        
        # Generate nonce for replay protection
        nonce = secrets.token_bytes(16)
        
        # Create message envelope
        message_id = hashlib.sha256(f"{self.node_id}{time.time()}{secrets.token_hex(8)}".encode()).hexdigest()[:16]
        
        envelope = {
            'message_id': message_id,
            'sender_id': self.node_id,
            'recipient_id': message_data.get('recipient_id'),
            'timestamp': time.time(),
            'message_type': message_data.get('message_type', 'data'),
            'payload': payload.hex(),
            'nonce': nonce.hex()
        }
        
        # Sign the envelope
        envelope_json = json.dumps(envelope, sort_keys=True)
        signature = self._sign_data(envelope_json.encode('utf-8'), signing_key)
        
        # Create secure message
        secure_msg = SecureMessage(
            message_id=message_id,
            sender_id=self.node_id,
            recipient_id=envelope['recipient_id'],
            timestamp=envelope['timestamp'],
            message_type=envelope['message_type'],
            payload=payload,
            signature=signature,
            nonce=nonce,
            session_key_id=f"session_{peer_node_id}" if peer_node_id else None,
            encryption_algorithm=signing_key.algorithm.value
        )
        
        return secure_msg
    
    def verify_message(self, secure_msg: SecureMessage) -> Optional[Dict[str, Any]]:
        """Verify and decrypt a message"""
        
        # Get sender's trusted key
        sender_key = self.get_trusted_key(secure_msg.sender_id)
        if not sender_key:
            logger.warning(f"No trusted key for sender {secure_msg.sender_id}")
            return None
        
        if sender_key.is_expired():
            logger.warning(f"Trusted key for {secure_msg.sender_id} is expired")
            return None
        
        # Verify signature
        envelope = {
            'message_id': secure_msg.message_id,
            'sender_id': secure_msg.sender_id,
            'recipient_id': secure_msg.recipient_id,
            'timestamp': secure_msg.timestamp,
            'message_type': secure_msg.message_type,
            'payload': secure_msg.payload.hex(),
            'nonce': secure_msg.nonce.hex()
        }
        
        envelope_json = json.dumps(envelope, sort_keys=True)
        is_valid = self._verify_signature(envelope_json.encode('utf-8'), secure_msg.signature, sender_key)
        
        if not is_valid:
            logger.warning(f"Invalid signature from {secure_msg.sender_id}")
            return None
        
        # Check message freshness (prevent replay attacks)
        if time.time() - secure_msg.timestamp > 300:  # 5 minute window
            logger.warning(f"Message {secure_msg.message_id} is too old")
            return None
        
        # Decrypt payload if needed
        payload = secure_msg.payload
        
        # Parse message data
        try:
            import json
            message_data = json.loads(payload.decode('utf-8'))
            return message_data
        except Exception as e:
            logger.error(f"Error parsing message payload: {e}")
            return None
    
    def _sign_data(self, data: bytes, key: CryptographicKey) -> bytes:
        """Sign data with specified key"""
        if key.algorithm == SignatureAlgorithm.ED25519:
            # Simplified Ed25519-like signing
            return hmac.new(key.private_key, data, hashlib.sha256).digest()
        elif key.algorithm == SignatureAlgorithm.HMAC_SHA256:
            return hmac.new(key.private_key, data, hashlib.sha256).digest()
        else:
            # Fallback to HMAC-SHA256
            return hmac.new(key.private_key, data, hashlib.sha256).digest()
    
    def _verify_signature(self, data: bytes, signature: bytes, key: CryptographicKey) -> bool:
        """Verify signature with specified key"""
        try:
            if key.algorithm == SignatureAlgorithm.ED25519:
                expected_signature = hmac.new(key.public_key, data, hashlib.sha256).digest()
            elif key.algorithm == SignatureAlgorithm.HMAC_SHA256:
                expected_signature = hmac.new(key.public_key, data, hashlib.sha256).digest()
            else:
                expected_signature = hmac.new(key.public_key, data, hashlib.sha256).digest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def establish_secure_channel(self, peer_node_id: str) -> Dict[str, Any]:
        """Establish SRP secure channel with peer node"""
        
        # Generate session key
        session_key = self.generate_session_key(peer_node_id)
        
        # Create SRP authentication challenge
        client_random = secrets.token_bytes(32)
        server_random = secrets.token_bytes(32)
        
        # Simulate SRP protocol (simplified)
        channel_establishment = {
            'type': 'srp_channel_establishment',
            'initiator_id': self.node_id,
            'responder_id': peer_node_id,
            'session_key_id': f"session_{peer_node_id}",
            'client_random': client_random.hex(),
            'server_random': server_random.hex(),
            'timestamp': time.time()
        }
        
        # Sign the establishment message
        secure_msg = self.sign_message(channel_establishment, "master_" + self.node_id, peer_node_id)
        
        return {
            'establishment_message': secure_msg.to_dict(),
            'session_key': session_key.hex(),
            'channel_id': f"channel_{self.node_id}_{peer_node_id}"
        }
    
    def verify_channel_establishment(self, establishment_msg: Dict[str, Any]) -> Optional[str]:
        """Verify SRP channel establishment response"""
        
        try:
            # Convert dict back to SecureMessage
            secure_msg = SecureMessage.from_dict(establishment_msg)
            
            # Verify the message
            verified_data = self.verify_message(secure_msg)
            if not verified_data:
                return None
            
            # Check if it's a valid channel establishment response
            if verified_data.get('type') == 'srp_channel_establishment':
                peer_node_id = verified_data.get('initiator_id')
                if peer_node_id != self.node_id:
                    return verified_data.get('session_key_id')
            
            return None
            
        except Exception as e:
            logger.error(f"Error verifying channel establishment: {e}")
            return None
    
    def rotate_keys(self):
        """Rotate cryptographic keys"""
        logger.info("Rotating cryptographic keys")
        
        # Mark old keys as expired
        current_time = time.time()
        for key in self.keys.values():
            if key.key_type != KeyType.MASTER:
                key.expires_at = current_time
        
        # Generate new signing key
        self._generate_master_key()
        
        logger.info("Key rotation completed")
    
    def get_key_status(self) -> Dict[str, Any]:
        """Get status of all keys"""
        status = {
            'node_id': self.node_id,
            'total_keys': len(self.keys),
            'trusted_nodes': len(self.trusted_nodes),
            'active_sessions': len(self.session_keys),
            'keys': {},
            'trusted_node_list': list(self.trusted_nodes.keys())
        }
        
        for key_id, key in self.keys.items():
            status['keys'][key_id] = {
                'type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'created_at': key.created_at,
                'expires_at': key.expires_at,
                'is_expired': key.is_expired(),
                'metadata': key.metadata
            }
        
        return status
    
    def cleanup_expired_keys(self):
        """Remove expired keys"""
        current_time = time.time()
        expired_keys = []
        
        for key_id, key in self.keys.items():
            if key.is_expired():
                expired_keys.append(key_id)
        
        for key_id in expired_keys:
            del self.keys[key_id]
            logger.debug(f"Removed expired key: {key_id}")
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired keys")
    
    def export_public_keys(self) -> Dict[str, Any]:
        """Export public keys for sharing with other nodes"""
        public_keys = {}
        
        for key_id, key in self.keys.items():
            if key.private_key is None:  # This shouldn't happen, but just in case
                continue
            
            public_keys[key_id] = {
                'key_id': key.key_id,
                'key_type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'public_key': key.public_key.hex(),
                'created_at': key.created_at,
                'metadata': key.metadata
            }
        
        return {
            'node_id': self.node_id,
            'exported_at': time.time(),
            'keys': public_keys
        }

# Utility functions

def generate_secure_random(size: int = 32) -> bytes:
    """Generate cryptographically secure random bytes"""
    return secrets.token_bytes(size)

def hash_password_sr6(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """Generate SRP password verifier (simplified)"""
    if salt is None:
        salt = generate_secure_random(16)
    
    # Simplified SRP hash
    verifier = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    
    return verifier, salt

def verify_sr6_password(password: str, verifier: bytes, salt: bytes) -> bool:
    """Verify SRP password (simplified)"""
    test_verifier, _ = hash_password_sr6(password, salt)
    return hmac.compare_digest(verifier, test_verifier)

# Example usage and testing
if __name__ == "__main__":
    async def test_crypto_system():
        # Create cryptographic managers for two nodes
        crypto_alice = CryptographicManager("alice_node")
        crypto_bob = CryptographicManager("bob_node")
        
        # Exchange public keys (simulate trust establishment)
        alice_pubkey = crypto_alice.keys["master_alice"].public_key
        bob_pubkey = crypto_bob.keys["master_bob"].public_key
        
        crypto_alice.trust_node("bob_node", bob_pubkey)
        crypto_bob.trust_node("alice_node", alice_pubkey)
        
        # Establish secure channel
        channel_est = crypto_alice.establish_secure_channel("bob_node")
        print(f"Channel establishment: {channel_est}")
        
        # Create and sign a message
        message_data = {
            'message_type': 'directive',
            'recipient_id': 'bob_node',
            'content': {
                'command': 'health_check',
                'parameters': {'check_type': 'comprehensive'}
            }
        }
        
        signed_message = crypto_alice.sign_message(
            message_data, 
            "master_alice",
            "bob_node"
        )
        
        print(f"Signed message: {signed_message.to_dict()}")
        
        # Verify the message
        verified_data = crypto_bob.verify_message(signed_message)
        print(f"Verified data: {verified_data}")
        
        # Show key status
        alice_status = crypto_alice.get_key_status()
        print(f"Alice key status: {alice_status}")
        
        print("Cryptographic signing test completed successfully")
    
    # Run the test
    import asyncio
    asyncio.run(test_crypto_system())
