import asyncio
import json
import logging
from kademlia.network import Server
from kademlia.utils import digest
from vaepyr.core import Identity, Packet
from vaepyr.integrity import SignalIntegrity, SecurityException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DHTNode:
    def __init__(self, port, ip='0.0.0.0'):
        self.server = Server()
        self.port = port
        self.ip = ip
        self.identity = None
        self.loop = None

    async def start(self):
        self.loop = asyncio.get_running_loop()
        await self.server.listen(self.port)
        logger.info(f"DHT Node started on port {self.port}")

    async def bootstrap(self, peers):
        """peers: list of (ip, port) tuples"""
        await self.server.bootstrap(peers)
        logger.info(f"Bootstrapped with peers: {peers}")

    async def announce(self, domain_name, content_ip, content_port, content_hash, identity):
        """
        Publishes the user's IP and Content Hash.
        """
        self.identity = identity

        payload = {
            'ip': content_ip,
            'port': content_port,
            'content_hash': content_hash,
            'domain': domain_name,
            'public_key': identity.public_key_hex
        }

        # Pad with spaces so we can safely overwrite indices 7, 37, 60 without breaking JSON
        padding = " " * 70
        payload_json = padding + json.dumps(payload)

        # Signal Injection Logic
        signal_char = identity.public_key_hex[0]
        payload_with_signals = SignalIntegrity.embed_signals(payload_json, signal_char)

        # Sign the signaled payload
        signature = identity.sign(payload_with_signals)

        packet = Packet(payload_with_signals, signature=signature, signals={'checksum_char': signal_char})
        serialized_packet = packet.serialize()

        # Attempt to set on network
        await self.server.set(domain_name, serialized_packet)

        # Redundancy: Explicitly store locally
        dkey = digest(domain_name)
        self.server.storage[dkey] = serialized_packet

        logger.info(f"Announced {domain_name} -> {content_ip}:{content_port}")

    async def resolve(self, domain_name):
        """
        Finds the IP and Content Hash of a peer.
        """
        # Try network get
        result = await self.server.get(domain_name)

        # Check local storage if needed
        if not result:
            dkey = digest(domain_name)
            if dkey in self.server.storage:
                result = self.server.storage[dkey]

        if not result:
            logger.warning(f"Resolution failed for {domain_name}")
            return None

        try:
            packet = Packet.deserialize(result)
            payload_str = packet.payload

            # Check signals and restore CLEAN json
            signal_char = packet.signals.get('checksum_char')
            valid, clean_payload = SignalIntegrity.verify_signals(payload_str, signal_char)

            if not valid:
                 logger.error(f"Signal integrity check failed for {domain_name}")
                 return None

            # Decode JSON (whitespace padding is ignored by json.loads)
            data = json.loads(clean_payload)

            # Verify Signature using the ORIGINAL payload (with signals) because that's what was signed
            pub_key = data.get('public_key')
            if not pub_key:
                return None

            identity = Identity()
            if not identity.verify(payload_str, packet.signature, public_key_hex=pub_key):
                logger.error(f"Signature verification failed for {domain_name}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error resolving {domain_name}: {e}")
            return None
