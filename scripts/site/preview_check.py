"""Loopback-only clean-URL preview with optional network-failure test modes."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
parser=argparse.ArgumentParser()
parser.add_argument('--root',default='docs/.vitepress/dist')
parser.add_argument('--base',default='/')
parser.add_argument('--port',type=int,default=4193)
parser.add_argument('--self-only',action='store_true')
parser.add_argument('--block-models',action='store_true')
args=parser.parse_args()
root=Path(args.root).resolve()
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=unquote(urlsplit(path).path)
        if not path.startswith(args.base): return str(root/'__missing_base__')
        target=(root/path[len(args.base):]).resolve()
        if not target.is_relative_to(root): return str(root/'__invalid_path__')
        if not target.exists() and Path(str(target)+'.html').is_file(): target=Path(str(target)+'.html')
        return str(target)
    def do_GET(self):
        if args.block_models and '/models/' in self.path:
            self.send_error(503,'Model temporarily unavailable for the failure test');return
        super().do_GET()
    def end_headers(self):
        if args.self_only:
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; worker-src 'self' blob:")
        self.send_header('Cache-Control','no-store')
        super().end_headers()
print(f'Preview http://127.0.0.1:{args.port}{args.base}',flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
