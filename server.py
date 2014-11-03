#!/usr/bin/python

import BaseHTTPServer, ssl, argparse, json, socket

target_server = "localhost"
target_port = 6659
target = 'irc://chat.freenode.net/#test'

def build_message(r):
  i = len(r['commits'])-1
  branch = r['ref'][r['ref'].rfind('/')+1:]
  return r['repository']['name'] + ': ' + r['commits'][i]['author']['name'] + ' ' + branch + ' * ' + r['after'] + ': ' + r['commits'][i]['message'] + ' - ' + r['commits'][i]['url']

def handle_request(request):
  msg = json.dumps({'to': target, 'privmsg': build_message(request)})
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg + "\n", (target_server, target_port))
  finally:
    sock.close()

class JSONServer(BaseHTTPServer.BaseHTTPRequestHandler):

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

  httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', args.port), JSONServer)
  if(args.ssl):
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile='server.key', certfile='server.crt', server_side=True)
  httpd.serve_forever()
