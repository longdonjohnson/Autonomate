import argparse
import asyncio
import os
import sys
import logging
from vaepyr.core import Identity
from vaepyr.dht import DHTNode
from vaepyr.integrity import GoldenState
from vaepyr.mesh import MeshNode
from vaepyr.resolver import DNSController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CLI')

def load_identity():
    if os.path.exists('identity.key'):
        return Identity.load('identity.key')
    else:
        logger.error("No identity found. Run 'init' first.")
        sys.exit(1)

def cmd_init(args):
    if os.path.exists('identity.key'):
        print("Identity already exists.")
        return

    identity = Identity()
    identity.save('identity.key')
    print(f"Identity generated. Public Key: {identity.public_key_hex}")

async def cmd_publish(args):
    identity = load_identity()
    directory = args.directory
    domain = args.domain

    if not os.path.exists(directory):
        logger.error(f"Directory {directory} does not exist.")
        return

    # 1. Calculate Hash
    try:
        content_hash = GoldenState.generate_merkle_root(directory)
    except Exception as e:
        logger.error(f"Error calculating hash: {e}")
        return

    logger.info(f"Content Hash: {content_hash}")

    # 2. Start DHT (Bootstrap from known peer or standalone if first?)
    # For publish, we need to connect to the network.
    # We assume we connect to a local running node or a known peer.
    # For MVP simplicity: We start a node, bootstrap to the provided peer, then announce.

    dht = DHTNode(port=args.port, ip=args.ip)
    await dht.start()

    if args.peer:
        peer_ip, peer_port = args.peer.split(':')
        await dht.bootstrap([(peer_ip, int(peer_port))])

    # 3. Start HTTP Server
    mesh = MeshNode(dht, directory)
    await mesh.start_http_server(args.http_port)

    # 4. Announce
    await dht.announce(domain, args.ip, args.http_port, content_hash, identity)

    print(f"Published {domain} successfully. Serving on {args.ip}:{args.http_port}")

    # Keep alive
    while True:
        await asyncio.sleep(3600)

async def cmd_serve(args):
    # Starts Resolver + Mesh + DHT (Full Node)
    identity = load_identity()

    dht = DHTNode(port=args.port, ip=args.ip)
    await dht.start()

    if args.peer:
        peer_ip, peer_port = args.peer.split(':')
        await dht.bootstrap([(peer_ip, int(peer_port))])

    # DNS
    dns = DNSController(dht, port=args.dns_port)
    dns.start()

    # Mesh (Mirroring logic would go here)
    # For now, we just participate in DHT.

    print(f"Node running. DNS on port {args.dns_port}. DHT on port {args.port}.")

    while True:
        await asyncio.sleep(3600)

async def cmd_connect(args):
    # Simple join and idle
    dht = DHTNode(port=args.port, ip=args.ip)
    await dht.start()

    peer_ip, peer_port = args.peer.split(':')
    await dht.bootstrap([(peer_ip, int(peer_port))])

    print(f"Connected to network via {args.peer}")

    while True:
        await asyncio.sleep(3600)

def main():
    parser = argparse.ArgumentParser(description="Væpyr CLI")
    subparsers = parser.add_subparsers(dest='command')

    # INIT
    subparsers.add_parser('init', help='Generate new identity')

    # PUBLISH
    p_pub = subparsers.add_parser('publish', help='Publish a site')
    p_pub.add_argument('directory', help='Content directory')
    p_pub.add_argument('domain', help='Domain name (e.g., site.vpr)')
    p_pub.add_argument('--ip', default='127.0.0.1', help='Public IP')
    p_pub.add_argument('--port', type=int, default=8468, help='DHT Port')
    p_pub.add_argument('--http-port', type=int, default=8080, help='HTTP Port')
    p_pub.add_argument('--peer', help='Bootstrap peer (ip:port)')

    # CONNECT
    p_con = subparsers.add_parser('connect', help='Join network')
    p_con.add_argument('peer', help='Peer IP:Port')
    p_con.add_argument('--port', type=int, default=8469, help='Local DHT Port')
    p_con.add_argument('--ip', default='127.0.0.1', help='Local IP')

    # SERVE
    p_serve = subparsers.add_parser('serve', help='Run full node (DNS + DHT)')
    p_serve.add_argument('--port', type=int, default=8468, help='DHT Port')
    p_serve.add_argument('--dns-port', type=int, default=5053, help='DNS Port')
    p_serve.add_argument('--ip', default='127.0.0.1', help='Local IP')
    p_serve.add_argument('--peer', help='Bootstrap peer (ip:port)')

    args = parser.parse_args()

    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'publish':
        asyncio.run(cmd_publish(args))
    elif args.command == 'connect':
        asyncio.run(cmd_connect(args))
    elif args.command == 'serve':
        asyncio.run(cmd_serve(args))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
