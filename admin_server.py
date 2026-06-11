from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import re
import os

PORT = 8081
REPO_DIR = r"C:\Users\sriva\Downloads\ZAXO-clothing"
HTML_PATH = os.path.join(REPO_DIR, "index.html")

class AdminHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            try:
                with open(HTML_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract the cats array
                match = re.search(r'const cats=(\[.*?\]);\s*const colours=\[', content, re.DOTALL)
                if match:
                    cats_str = match.group(1)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    # We send the JS string inside a JSON object so the frontend can eval it
                    self.wfile.write(json.dumps({'cats_js': cats_str}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Could not find cats array in index.html")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/data':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                new_cats_str = data['cats_js']
                
                with open(HTML_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the old cats array
                new_content = re.sub(r'const cats=\[.*?\];\s*const colours=\[', f'const cats={new_cats_str};\n\nconst colours=[', content, flags=re.DOTALL)
                
                with open(HTML_PATH, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    os.chdir(REPO_DIR) # Serve files from the repo dir
    server = HTTPServer(('localhost', PORT), AdminHandler)
    print(f"Admin server running on http://localhost:{PORT}")
    server.serve_forever()
