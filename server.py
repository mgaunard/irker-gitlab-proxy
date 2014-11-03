#!/usr/bin/python

import BaseHTTPServer, ssl, argparse, json, datetime

def handle_request(request):
  print request

def json_handler(obj):
  if hasattr(obj, 'isoformat'):
    return obj.isoformat()
  else:
    raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

class JSONRPCServer(BaseHTTPServer.BaseHTTPRequestHandler):

  def __init__(self, request, client_address, server):
    BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

  def bad_request(self, data=None, status=400):
    raise RuntimeError("Bad request")

  def do_POST(self):
    if(not 'content-type' in self.headers or self.headers['content-type'] != 'application/json'):
      self.bad_request('Incorrect Content-Type')

    if('content-length' in self.headers):
      data = self.rfile.read(int(self.headers['content-length']))
    else:
      data = self.rfile.read()
    try:
      request = json.loads(data)
    except:
      self.bad_request(data)

    self.send_response(200)
    self.send_header('Content-Type', 'application/json')

    try:
      handle_request(request)
    except BaseException as e:
      print request
      print e

if __name__ == '__main__':
  '''
  IRKER-GITLAB proxy
  '''
  parser = argparse.ArgumentParser(description="IRKER-GITLAB proxy.")
  parser.add_argument('port', type=int, help='port to listen on')
  parser.add_argument('-s', '--ssl', action="store_true", help="whether to use SSL to make it HTTPS")

  args = parser.parse_args()

  httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', args.port), JSONRPCServer)
  if(args.ssl):
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile='server.key', certfile='server.crt', server_side=True)
  httpd.serve_forever()
