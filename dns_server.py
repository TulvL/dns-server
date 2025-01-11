from dnslib import DNSRecord,QTYPE , RR, A, AAAA
from dnslib.server import DNSServer, DNSHandler, BaseResolver


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
                    reply.add_answer(RR(qname,QTYPE.A , rdata=A(ip), ttl=300))
                else:
                    reply.header.rcode = 0
            else:
                # 如果格式不匹配，返回 NXDOMAIN
                reply.header.rcode = 3  # NXDOMAIN

        elif qname.endswith(base_domain):
            if qtype==1:
                reply.add_answer(RR(qname,QTYPE.A , rdata=A("104.21.55.142"), ttl=300))
                reply.add_answer(RR(qname,QTYPE.A, rdata=A("172.67.149.32"), ttl=300))
            elif qtype==28:
                reply.add_answer(RR(qname,QTYPE.AAAA, rdata=AAAA("2606:4700:3034::ac43:9520"), ttl=300))
                reply.add_answer(RR(qname,QTYPE.AAAA, rdata=AAAA("2606:4700:3030::6815:378e"), ttl=300))
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
