"""
Encryption Service for OpenLens

Provides data encryption and decryption:
- Symmetric encryption (AES)
- Asymmetric encryption (RSA)
- Hashing
- Key management
- Data signing
"""

import os
import base64
import hashlib
import json
import secrets
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend


@dataclass
class EncryptionConfig:
    """Configuration for encryption service."""
    symmetric_key: str = ''  # Base64 encoded symmetric key
    private_key_path: str = '/etc/openlens/private_key.pem'
    public_key_path: str = '/etc/openlens/public_key.pem'
    key_derivation_salt: str = ''
    key_derivation_iterations: int = 100000
    hash_algorithm: str = 'SHA256'
    symmetric_algorithm: str = 'AES'
    symmetric_key_size: int = 256  # bits
    asymmetric_key_size: int = 2048  # bits
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symmetric_key': '*****' if self.symmetric_key else '',
            'private_key_path': self.private_key_path,
            'public_key_path': self.public_key_path,
            'key_derivation_salt': '*****' if self.key_derivation_salt else '',
            'key_derivation_iterations': self.key_derivation_iterations,
            'hash_algorithm': self.hash_algorithm,
            'symmetric_algorithm': self.symmetric_algorithm,
            'symmetric_key_size': self.symmetric_key_size,
            'asymmetric_key_size': self.asymmetric_key_size,
        }


@dataclass
class EncryptionResult:
    """Result of encryption."""
    ciphertext: str
    iv: str = ''
    tag: str = ''
    algorithm: str = ''
    key_id: str = ''
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'ciphertext': self.ciphertext,
            'iv': self.iv,
            'tag': self.tag,
            'algorithm': self.algorithm,
            'key_id': self.key_id,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class DecryptionResult:
    """Result of decryption."""
    plaintext: str
    algorithm: str = ''
    key_id: str = ''
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'plaintext': self.plaintext,
            'algorithm': self.algorithm,
            'key_id': self.key_id,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class HashResult:
    """Result of hashing."""
    hash_value: str
    algorithm: str = ''
    salt: str = ''
    iterations: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hash_value': self.hash_value,
            'algorithm': self.algorithm,
            'salt': self.salt,
            'iterations': self.iterations,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class KeyPair:
    """Represents a key pair."""
    private_key: Any
    public_key: Any
    key_id: str = ''
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'key_id': self.key_id,
            'created_at': self.created_at.isoformat(),
        }


class EncryptionService:
    """
    Encryption service for OpenLens.
    
    Provides:
    - Symmetric encryption (AES)
    - Asymmetric encryption (RSA)
    - Hashing
    - Key management
    - Data signing
    """
    
    def __init__(self, config: EncryptionConfig = None):
        """
        Initialize the encryption service.
        
        Args:
            config: EncryptionConfig instance.
        """
        self.config = config or EncryptionConfig()
        self._symmetric_key = None
        self._private_key = None
        self._public_key = None
        self._key_cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Load or generate keys
        self._load_or_generate_keys()
    
    def _load_or_generate_keys(self):
        """Load or generate encryption keys."""
        # Load symmetric key
        if self.config.symmetric_key:
            try:
                self._symmetric_key = base64.b64decode(self.config.symmetric_key)
            except:
                self._symmetric_key = None
        
        if not self._symmetric_key:
            self._symmetric_key = self._generate_symmetric_key()
        
        # Load or generate asymmetric keys
        if os.path.exists(self.config.private_key_path) and os.path.exists(self.config.public_key_path):
            try:
                self._load_asymmetric_keys()
            except Exception as e:
                print(f"Error loading asymmetric keys: {e}")
                self._generate_asymmetric_keys()
        else:
            self._generate_asymmetric_keys()
    
    def _generate_symmetric_key(self) -> bytes:
        """Generate a symmetric key."""
        key_size = self.config.symmetric_key_size // 8  # Convert bits to bytes
        return secrets.token_bytes(key_size)
    
    def _generate_asymmetric_keys(self):
        """Generate asymmetric key pair."""
        # Generate private key
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.config.asymmetric_key_size,
            backend=default_backend()
        )
        
        # Generate public key
        self._public_key = self._private_key.public_key()
        
        # Save keys to files
        self._save_asymmetric_keys()
    
    def _load_asymmetric_keys(self):
        """Load asymmetric keys from files."""
        # Load private key
        with open(self.config.private_key_path, 'rb') as f:
            self._private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        # Load public key
        with open(self.config.public_key_path, 'rb') as f:
            self._public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
    
    def _save_asymmetric_keys(self):
        """Save asymmetric keys to files."""
        # Create directory if it doesn't exist
        private_dir = os.path.dirname(self.config.private_key_path)
        public_dir = os.path.dirname(self.config.public_key_path)
        
        if private_dir and not os.path.exists(private_dir):
            os.makedirs(private_dir, exist_ok=True)
        if public_dir and not os.path.exists(public_dir):
            os.makedirs(public_dir, exist_ok=True)
        
        # Save private key
        with open(self.config.private_key_path, 'wb') as f:
            pem = self._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            f.write(pem)
        
        # Save public key
        with open(self.config.public_key_path, 'wb') as f:
            pem = self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            f.write(pem)
    
    def encrypt_symmetric(self, plaintext: str, key: bytes = None, 
                        key_id: str = 'default') -> EncryptionResult:
        """
        Encrypt data using symmetric encryption (AES-GCM).
        
        Args:
            plaintext: Data to encrypt.
            key: Symmetric key (None for default).
            key_id: Key identifier.
            
        Returns:
            EncryptionResult.
        """
        key = key or self._symmetric_key
        
        if not key:
            raise ValueError("No symmetric key available")
        
        # Generate IV
        iv = secrets.token_bytes(12)  # 96 bits for GCM
        
        # Encrypt
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        
        ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            iv=base64.b64encode(iv).decode('utf-8'),
            tag=base64.b64encode(encryptor.tag).decode('utf-8'),
            algorithm='AES-GCM',
            key_id=key_id,
        )
    
    def decrypt_symmetric(self, ciphertext: str, iv: str, tag: str, 
                        key: bytes = None, key_id: str = 'default') -> DecryptionResult:
        """
        Decrypt data using symmetric encryption (AES-GCM).
        
        Args:
            ciphertext: Encrypted data.
            iv: Initialization vector.
            tag: Authentication tag.
            key: Symmetric key (None for default).
            key_id: Key identifier.
            
        Returns:
            DecryptionResult.
        """
        key = key or self._symmetric_key
        
        if not key:
            raise ValueError("No symmetric key available")
        
        # Decode from base64
        ciphertext_bytes = base64.b64decode(ciphertext)
        iv_bytes = base64.b64decode(iv)
        tag_bytes = base64.b64decode(tag)
        
        # Decrypt
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv_bytes, tag_bytes),
            backend=default_backend()
        ).decryptor()
        
        plaintext = decryptor.update(ciphertext_bytes) + decryptor.finalize()
        
        return DecryptionResult(
            plaintext=plaintext.decode('utf-8'),
            algorithm='AES-GCM',
            key_id=key_id,
        )
    
    def encrypt_asymmetric(self, plaintext: str, public_key: Any = None, 
                         key_id: str = 'default') -> EncryptionResult:
        """
        Encrypt data using asymmetric encryption (RSA-OAEP).
        
        Args:
            plaintext: Data to encrypt.
            public_key: Public key (None for default).
            key_id: Key identifier.
            
        Returns:
            EncryptionResult.
        """
        public_key = public_key or self._public_key
        
        if not public_key:
            raise ValueError("No public key available")
        
        # Encrypt
        ciphertext = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptionResult(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            algorithm='RSA-OAEP',
            key_id=key_id,
        )
    
    def decrypt_asymmetric(self, ciphertext: str, private_key: Any = None, 
                         key_id: str = 'default') -> DecryptionResult:
        """
        Decrypt data using asymmetric encryption (RSA-OAEP).
        
        Args:
            ciphertext: Encrypted data.
            private_key: Private key (None for default).
            key_id: Key identifier.
            
        Returns:
            DecryptionResult.
        """
        private_key = private_key or self._private_key
        
        if not private_key:
            raise ValueError("No private key available")
        
        # Decode from base64
        ciphertext_bytes = base64.b64decode(ciphertext)
        
        # Decrypt
        plaintext = private_key.decrypt(
            ciphertext_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return DecryptionResult(
            plaintext=plaintext.decode('utf-8'),
            algorithm='RSA-OAEP',
            key_id=key_id,
        )
    
    def hash_data(self, data: str, salt: str = None, 
                  iterations: int = None) -> HashResult:
        """
        Hash data using PBKDF2.
        
        Args:
            data: Data to hash.
            salt: Salt (None for random).
            iterations: Number of iterations.
            
        Returns:
            HashResult.
        """
        salt = salt or secrets.token_hex(16)
        iterations = iterations or self.config.key_derivation_iterations
        
        # Get hash algorithm
        hash_algorithm = getattr(hashes, self.config.hash_algorithm)()
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hash_algorithm,
            length=32,
            salt=salt.encode('utf-8'),
            iterations=iterations,
            backend=default_backend()
        )
        
        key = kdf.derive(data.encode('utf-8'))
        
        return HashResult(
            hash_value=base64.b64encode(key).decode('utf-8'),
            algorithm=self.config.hash_algorithm,
            salt=salt,
            iterations=iterations,
        )
    
    def verify_hash(self, data: str, hash_value: str, salt: str, 
                    iterations: int = None) -> bool:
        """
        Verify a hash.
        
        Args:
            data: Data to verify.
            hash_value: Hash value to compare.
            salt: Salt used in hashing.
            iterations: Number of iterations.
            
        Returns:
            True if hash matches.
        """
        # Hash the data with the same parameters
        result = self.hash_data(data, salt, iterations)
        
        # Compare
        return secrets.compare_digest(result.hash_value, hash_value)
    
    def sign_data(self, data: str, private_key: Any = None) -> str:
        """
        Sign data using RSA.
        
        Args:
            data: Data to sign.
            private_key: Private key (None for default).
            
        Returns:
            Base64 encoded signature.
        """
        private_key = private_key or self._private_key
        
        if not private_key:
            raise ValueError("No private key available")
        
        # Sign
        signature = private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, data: str, signature: str, 
                        public_key: Any = None) -> bool:
        """
        Verify a signature.
        
        Args:
            data: Data to verify.
            signature: Signature to verify.
            public_key: Public key (None for default).
            
        Returns:
            True if signature is valid.
        """
        public_key = public_key or self._public_key
        
        if not public_key:
            raise ValueError("No public key available")
        
        # Decode signature
        signature_bytes = base64.b64decode(signature)
        
        try:
            public_key.verify(
                signature_bytes,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False
    
    def generate_key_pair(self, key_size: int = None) -> KeyPair:
        """
        Generate a new RSA key pair.
        
        Args:
            key_size: Key size in bits.
            
        Returns:
            KeyPair.
        """
        key_size = key_size or self.config.asymmetric_key_size
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Generate public key
        public_key = private_key.public_key()
        
        key_id = str(secrets.token_hex(8))
        
        key_pair = KeyPair(
            private_key=private_key,
            public_key=public_key,
            key_id=key_id,
        )
        
        # Cache the key pair
        self._key_cache[key_id] = key_pair
        
        return key_pair
    
    def get_key_pair(self, key_id: str) -> Optional[KeyPair]:
        """
        Get a key pair by ID.
        
        Args:
            key_id: Key ID.
            
        Returns:
            KeyPair or None.
        """
        return self._key_cache.get(key_id)
    
    def encrypt_with_key_id(self, plaintext: str, key_id: str, 
                           algorithm: str = 'symmetric') -> EncryptionResult:
        """
        Encrypt data using a specific key ID.
        
        Args:
            plaintext: Data to encrypt.
            key_id: Key ID.
            algorithm: Encryption algorithm ('symmetric' or 'asymmetric').
            
        Returns:
            EncryptionResult.
        """
        if algorithm == 'symmetric':
            # For now, use the default symmetric key
            # In a real implementation, we would look up the key
            return self.encrypt_symmetric(plaintext, key_id=key_id)
        elif algorithm == 'asymmetric':
            key_pair = self.get_key_pair(key_id)
            if not key_pair:
                raise ValueError(f"Key pair {key_id} not found")
            return self.encrypt_asymmetric(plaintext, key_pair.public_key, key_id=key_id)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def decrypt_with_key_id(self, ciphertext: str, key_id: str, 
                           algorithm: str = 'symmetric', 
                           iv: str = None, tag: str = None) -> DecryptionResult:
        """
        Decrypt data using a specific key ID.
        
        Args:
            ciphertext: Encrypted data.
            key_id: Key ID.
            algorithm: Encryption algorithm ('symmetric' or 'asymmetric').
            iv: Initialization vector (for symmetric).
            tag: Authentication tag (for symmetric).
            
        Returns:
            DecryptionResult.
        """
        if algorithm == 'symmetric':
            # For now, use the default symmetric key
            return self.decrypt_symmetric(ciphertext, iv, tag, key_id=key_id)
        elif algorithm == 'asymmetric':
            key_pair = self.get_key_pair(key_id)
            if not key_pair:
                raise ValueError(f"Key pair {key_id} not found")
            return self.decrypt_asymmetric(ciphertext, key_pair.private_key, key_id=key_id)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def get_public_key_pem(self) -> str:
        """
        Get the default public key in PEM format.
        
        Returns:
            PEM encoded public key.
        """
        if not self._public_key:
            return ''
        
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    
    def get_private_key_pem(self) -> str:
        """
        Get the default private key in PEM format.
        
        Returns:
            PEM encoded private key.
        """
        if not self._private_key:
            return ''
        
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
    
    def get_symmetric_key_base64(self) -> str:
        """
        Get the default symmetric key in base64.
        
        Returns:
            Base64 encoded symmetric key.
        """
        if not self._symmetric_key:
            return ''
        
        return base64.b64encode(self._symmetric_key).decode('utf-8')


# Global encryption service instance
encryption_service = EncryptionService()
