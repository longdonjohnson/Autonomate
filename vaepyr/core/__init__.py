import json
import time
import base64
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder, Base64Encoder

class Identity:
    def __init__(self, private_key_hex=None):
        if private_key_hex:
            self.signing_key = SigningKey(private_key_hex, encoder=HexEncoder)
        else:
            self.signing_key = SigningKey.generate()

        self.verify_key = self.signing_key.verify_key
        self.public_key_hex = self.verify_key.encode(encoder=HexEncoder).decode('utf-8')

    def save(self, filepath):
        with open(filepath, 'w') as f:
            f.write(self.signing_key.encode(encoder=HexEncoder).decode('utf-8'))

    @classmethod
    def load(cls, filepath):
        with open(filepath, 'r') as f:
            key_hex = f.read().strip()
        return cls(private_key_hex=key_hex)

    def sign(self, data):
        """Sign bytes data."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.signing_key.sign(data).signature

    def verify(self, data, signature, public_key_hex=None):
        """Verify signature."""
        if isinstance(data, str):
            data = data.encode('utf-8')

        if public_key_hex:
            verify_key = VerifyKey(public_key_hex, encoder=HexEncoder)
        else:
            verify_key = self.verify_key

        try:
            verify_key.verify(data, signature)
            return True
        except:
            return False

class Packet:
    def __init__(self, payload, signature=None, timestamp=None, signals=None):
        self.payload = payload
        self.signature = signature
        self.timestamp = timestamp or time.time()
        self.signals = signals or {}

    def to_dict(self):
        return {
            'payload': self.payload,
            'signature': base64.b64encode(self.signature).decode('utf-8') if self.signature else None,
            'timestamp': self.timestamp,
            'signals': self.signals
        }

    @classmethod
    def from_dict(cls, data):
        signature = None
        if data.get('signature'):
            signature = base64.b64decode(data['signature'])

        return cls(
            payload=data['payload'],
            signature=signature,
            timestamp=data.get('timestamp'),
            signals=data.get('signals')
        )

    def serialize(self):
        return json.dumps(self.to_dict())

    @classmethod
    def deserialize(cls, json_str):
        return cls.from_dict(json.loads(json_str))
