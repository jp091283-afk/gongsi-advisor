import http.server
import urllib.request
import json
import ssl
import os

PORT = int(os.environ.get('PORT', 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = '공시어드바이저_최종.html'
HTML_PATH = os.path.join(BASE_DIR, HTML_FILE)

print(f'서버 시작: port={PORT}', flush=True)
print(f'HTML: {HTML_PATH}', flush=True)
print(f'HTML 존재: {os.path.exists(HTML_PATH)}', flush=True)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # DART API 프록시
        if self.path.startswith('/api/dart'):
            query = self.path[9:]
            dart_url = 'https://opendart.fss.or.kr/api/list.json' + query
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(dart_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120',
                'Accept': 'application/json',
            })
            try:
                with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                    body = r.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
            except urllib.error.HTTPError as e:
                err = e.read().decode('utf-8', 'ignore')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'HTTP_'+str(e.code), 'message': err[:200]}).encode())
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ERR', 'message': str(e)}).encode())
            return

        # 루트 → 메인 HTML
        req_path = self.path.split('?')[0]
        if req_path == '/':
            try:
                with open(HTML_PATH, 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            return

        # 기타 파일
        filepath = os.path.join(BASE_DIR, req_path.lstrip('/'))
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                body = f.read()
            self.send_response(200)
            ext = filepath.rsplit('.', 1)[-1].lower()
            ct = {'html': 'text/html; charset=utf-8', 'js': 'application/javascript', 'css': 'text/css'}.get(ext, 'application/octet-stream')
            self.send_header('Content-Type', ct)
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass

print(f'Running on 0.0.0.0:{PORT}', flush=True)
server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()
