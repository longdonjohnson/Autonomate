import asyncio
import os
import sys
import logging
import hashlib
from vaepyr.dht import DHTNode
from vaepyr.mesh import MeshNode
from vaepyr.core import Identity
from vaepyr.integrity import GoldenState

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Genesis')

async def bootstrap_network(ip='127.0.0.1', port=8468):
    """
    Starts the first DHT node (Seed).
    """
    # 1. Start DHT
    dht = DHTNode(port, ip=ip)
    await dht.start()

    # 2. Print Connection Info
    print(f"\n{'='*40}")
    print(f"GENESIS NODE STARTED")
    print(f"IP: {ip}")
    print(f"Port: {port}")
    print(f"Join Command: connect {ip} {port}")
    print(f"{'='*40}\n")

    # 3. Self-Test
    await perform_self_test(dht, ip, port)

    # Keep running
    while True:
        await asyncio.sleep(3600)

async def perform_self_test(dht, ip, port):
    logger.info("Performing Self-Test...")

    # Create a dummy Hello World site
    test_dir = "hello_world_site"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    index_path = os.path.join(test_dir, "index.html")
    with open(index_path, "w") as f:
        f.write("<h1>Hello World from Væpyr!</h1>")

    # Generate Identity
    identity = Identity()

    # Calculate Hash
    # We use the same method CLI uses now: GoldenState.generate_merkle_root
    content_hash = GoldenState.generate_merkle_root(test_dir)

    # Announce
    domain = "hello.vpr"
    # We use a mesh node to verify serving capability
    mesh = MeshNode(dht, test_dir)
    http_port = 8080
    await mesh.start_http_server(http_port)

    await dht.announce(domain, ip, http_port, content_hash, identity)

    # Resolve and Check
    logger.info(f"Resolving {domain}...")
    record = await dht.resolve(domain)

    if record and record['content_hash'] == content_hash:
        logger.info("Self-Test PASSED: Domain resolved and hash matches.")

        # Verify Stream Logic (Fetch from self)
        # We try to fetch index.html (default)
        try:
            fetched_content = await mesh.fetch_content(domain)
            logger.info(f"Fetched content length: {len(fetched_content)}")
            if b"Hello World" in fetched_content:
                 logger.info("Content Verified: SUCCESS")
            else:
                 logger.error("Content Verification Failed: Content mismatch.")
        except Exception as e:
            logger.error(f"Content Verification Failed: {e}")
            sys.exit(1) # Fail the test
    else:
        logger.error("Self-Test FAILED: Resolution mismatch or failure.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(bootstrap_network())
    except KeyboardInterrupt:
        pass
