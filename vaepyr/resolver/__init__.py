import asyncio
import logging
from dnslib import DNSRecord, QTYPE, RR, A
from dnslib.server import DNSServer, BaseResolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalDNS(BaseResolver):
    def __init__(self, dht_node, forward_ip='1.1.1.1'):
        self.dht = dht_node
        self.forward_ip = forward_ip

    def resolve(self, request, handler):
        qname = str(request.q.qname)
        qtype = QTYPE[request.q.qtype]

        reply = request.reply()

        if qname.endswith('.vpr.'):
            # Intercept .vpr queries
            domain = qname.rstrip('.')
            logger.info(f"Intercepted .vpr query: {domain}")

            try:
                # Assuming dht.loop is set by dht.start()
                future = asyncio.run_coroutine_threadsafe(self.dht.resolve(domain), self.dht.loop)
                record = future.result(timeout=5)

                if record:
                    ip = record['ip']
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=60))
                else:
                    # NXDOMAIN
                    reply.header.rcode = 3
            except Exception as e:
                logger.error(f"DNS Resolution Error: {e}")
                reply.header.rcode = 2 # SERVFAIL

        else:
            # Forward to 1.1.1.1 (Standard DNS)
            try:
                a = DNSRecord.parse(DNSRecord.question(qname).send(self.forward_ip, 53, tcp=False, timeout=2))
                for rr in a.rr:
                    reply.add_answer(rr)
            except Exception as e:
                logger.error(f"Forwarding Error: {e}")

        return reply

class DNSController:
    def __init__(self, dht_node, port=5053):
        self.resolver = LocalDNS(dht_node)
        self.server = DNSServer(self.resolver, port=port, address="127.0.0.1", tcp=False)
        self.port = port

    def start(self):
        logger.info(f"Starting DNS Interceptor on 127.0.0.1:{self.port}")
        self.server.start_thread()

    def stop(self):
        self.server.stop()
