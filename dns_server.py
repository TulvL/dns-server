from dnslib import DNSRecord, RR, A, CNAME
from dnslib.server import DNSServer, DNSHandler, BaseResolver
import socket
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("DNS")


class DynamicResolver(BaseResolver):
    def resolve(self, request, handler):
        # 获取请求的域名
        qname = str(request.q.qname).lower().strip(".")
        reply = request.reply()
        qtype = request.q.qtype
        #logger.debug(f"Received query: {qname}, type: {qtype}")
        
        base_domain = "flares.cloud"
            
        # 动态解析 a-b-c-d 到 a.b.c.d
        if qname.endswith(".ip." + base_domain):
            parts = qname.split(".")[0].split("-")
            #print(parts)
            if len(parts) == 4 and all(p.isdigit() for p in parts):
                # 解析为 IPv4 地址
                if qtype==1:
                    ip = ".".join(parts)
                    reply.add_answer(RR(qname, rdata=A(ip), ttl=300))
                else:
                    reply.header.rcode = 0
            else:
                # 如果格式不匹配，返回 NXDOMAIN
                reply.header.rcode = 3  # NXDOMAIN

        elif qname.endswith(base_domain):
            if qtype==1:
                reply.add_answer(RR(qname, rdata=A("104.28.30.218"), ttl=300))
                reply.add_answer(RR(qname, rdata=A("104.28.31.218"), ttl=300))
                reply.add_answer(RR(qname, rdata=A("172.67.166.240"), ttl=300))
            else:
                reply.header.rcode = 0


        else:
            # 如果不属于已定义的域，返回 NXDOMAIN
            reply.header.rcode = 3  # NXDOMAIN

        return reply

if __name__ == "__main__":
    # 监听的地址和端口
    resolver = DynamicResolver()
    server = DNSServer(resolver, port=53, address="::")
    print("Starting DNS server")
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
