#!/usr/bin/env python3
"""Preview the same /darkecho/ base path used by GitHub Pages."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import os
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def _serve(self,head=False):
  path=urlsplit(self.path).path
  if path in ['/','/darkecho']:
   self.send_response(302);self.send_header('Location','/darkecho/');self.end_headers();return
  if path.startswith('/darkecho/'):
   self.path=self.path[len('/darkecho'):]
   return super().do_HEAD() if head else super().do_GET()
  self.send_error(404)
 def do_GET(self):self._serve()
 def do_HEAD(self):self._serve(head=True)
 def send_error(self,code,message=None,explain=None):
  if code==404 and (ROOT/'404.html').exists():
   body=(ROOT/'404.html').read_bytes();self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers()
   if self.command!='HEAD':self.wfile.write(body)
  else:super().send_error(code,message,explain)
if __name__=='__main__':
 port=int(os.environ.get('PORT','4173'))
 print(f'Preview at http://0.0.0.0:{port}/darkecho/',flush=True)
 ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
