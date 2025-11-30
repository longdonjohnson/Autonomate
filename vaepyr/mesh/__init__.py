import asyncio
import logging
import aiohttp.web
import os
import hashlib
from vaepyr.dht import DHTNode
from vaepyr.integrity import GoldenState, SecurityException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeshNode:
    def __init__(self, dht_node: DHTNode, content_dir):
        self.dht = dht_node
        self.content_dir = content_dir
        self.app = aiohttp.web.Application()
        self.app.router.add_get('/{path:.*}', self.handle_request)
        self.runner = None
        self.site = None

    async def start_http_server(self, port):
        self.runner = aiohttp.web.AppRunner(self.app)
        await self.runner.setup()
        self.site = aiohttp.web.TCPSite(self.runner, '0.0.0.0', port)
        await self.site.start()
        logger.info(f"Mesh HTTP Server started on port {port} serving {self.content_dir}")

    async def handle_request(self, request):
        path = request.match_info.get('path', '')
        if not path or path == '/':
            path = 'index.html'

        path = path.lstrip('/')

        filepath = os.path.join(self.content_dir, path)

        # Security: Prevent directory traversal
        if not os.path.abspath(filepath).startswith(os.path.abspath(self.content_dir)):
            return aiohttp.web.Response(status=403, text="Access Denied")

        if os.path.exists(filepath) and os.path.isfile(filepath):
            return aiohttp.web.FileResponse(filepath)
        else:
            return aiohttp.web.Response(status=404, text="Not Found")

    async def fetch_content(self, domain_name, path='/'):
        """
        Client logic: Resolve -> Fetch -> Verify -> Failover.
        Fetches the specific file at 'path'.
        Note: For MVP, verification against the Root Hash is only possible if
        the Root Hash == File Hash (single file site).
        Multi-file site verification would require `fetch_site`.
        """
        record = await self.dht.resolve(domain_name)
        if not record:
            raise Exception("Domain not found")

        target_ip = record['ip']
        target_port = record['port']
        expected_hash = record['content_hash']

        try:
            return await self._download_and_verify(target_ip, target_port, path, expected_hash)
        except (SecurityException, Exception) as e:
            logger.warning(f"Primary fetch failed: {e}. Attempting failover to mirrors.")
            return await self._attempt_failover(domain_name, path, expected_hash)

    async def fetch_site(self, domain_name, output_dir):
        """
        Fetches the entire site (all files) to verify the Merkle Root.
        For MVP, we assume we can crawl or index the site.
        Since we don't have a manifest, this is tricky.
        This is a placeholder to show intent for multi-file verification.
        """
        # MVP Implementation: Just fetch index.html and warn if hash mismatch
        # Real implementation: Fetch manifest, download all, hash all, verify root.
        pass

    async def _attempt_failover(self, domain_name, path, expected_hash):
        """
        Query DHT for mirrors and attempt to fetch.
        """
        mirror_key = f"mirror:{domain_name}"
        mirror_record = await self.dht.resolve(mirror_key)

        if not mirror_record:
            logger.error("No mirrors found.")
            raise Exception("Content unavailable (Primary failed, No mirrors)")

        mirror_ip = mirror_record.get('ip')
        mirror_port = mirror_record.get('port')

        if not mirror_ip or not mirror_port:
             raise Exception("Invalid mirror record")

        logger.info(f"Failover: Trying mirror {mirror_ip}:{mirror_port}")
        return await self._download_and_verify(mirror_ip, mirror_port, path, expected_hash)

    async def _download_and_verify(self, ip, port, path, expected_hash):
        url = f"http://{ip}:{port}/{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP Error {resp.status}")

                content = await resp.read()

                # Verify Integrity
                # If expected_hash is the Merkle Root of multiple files,
                # this check will fail for a single file unless it happens to match.
                # However, for the 'Hello World' single-file case (MVP test), it matches.
                # We enforce it strictly as per "Golden State" requirement.
                GoldenState.verify_stream(content, expected_hash)

                return content
