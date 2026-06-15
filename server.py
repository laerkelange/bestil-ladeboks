import http.server, urllib.request, os, re

PLACEHOLDER_SVG = b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
<circle cx="20" cy="20" r="19" fill="#f7efeb" stroke="#e6d9d2" stroke-width="1.5"/>
<text x="20" y="25" text-anchor="middle" font-family="Arial" font-size="14" fill="#bfb1aa">?</text>
</svg>'''

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/proxy/sponsor?'):
            qs = self.path.split('?', 1)[1]
            self._proxy(f'https://www.ok.dk/api/sponsor/agreements?{qs}', 'application/json')
        elif self.path.startswith('/proxy/logo/'):
            nr = self.path.split('/proxy/logo/')[1].split('?')[0]
            if re.match(r'^\d+$', nr):
                self._proxy_logo(f'https://cdn.ok.dk/wok/sponsor-klublogoer/{nr}.svg')
            else:
                self.send_error(400)
        else:
            super().do_GET()

    def _proxy(self, url, content_type):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = r.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(502, str(e))

    def _proxy_logo(self, url):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.ok.dk/'
            })
            with urllib.request.urlopen(req, timeout=4) as r:
                if r.status == 200:
                    data = r.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/svg+xml')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    self.end_headers()
                    self.wfile.write(data)
                    return
        except Exception:
            pass
        # Fallback placeholder
        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(PLACEHOLDER_SVG)

    def log_message(self, *a): pass

os.chdir(os.path.dirname(os.path.abspath(__file__)))
httpd = http.server.HTTPServer(('', 8765), Handler)
print('Serving on :8765')
httpd.serve_forever()
