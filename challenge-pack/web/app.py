"""Four intentionally simple, isolated beginner CTF Web services."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64, os

CHALLENGE = os.environ.get("CHALLENGE", "w1")
FLAG = {
    "w1": "YITCTF{comments_are_source_code}",
    "w2": "YITCTF{cookies_are_client_side}",
    "w3": "YITCTF{parameterized_queries_win}",
    "w4": "YITCTF{robots_remember_paths}",
    "w5": "YITCTF{html_comments_hide_things}",
    "w6": "YITCTF{parameters_can_change_things}",
    "w7": "YITCTF{client_side_is_not_secret}"
}[CHALLENGE]

class App(BaseHTTPRequestHandler):
    def send(self, code=200, body="", content_type="text/html; charset=utf-8", headers=None):
        self.send_response(code); self.send_header("Content-Type", content_type)
        for k, v in (headers or {}).items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(body.encode())
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if CHALLENGE == "w1":
            return self.send(body=f"<h1>YIT Noticeboard</h1><p>Nothing to see here.</p><!-- flag: {FLAG} -->")
        if CHALLENGE == "w2":
            role = self.headers.get("Cookie", "").split("role=", 1)[-1].split(";", 1)[0]
            try: role = base64.b64decode(role).decode()
            except Exception: role = "guest"
            if role == "admin": return self.send(body=f"<h1>Admin dashboard</h1><p>{FLAG}</p>")
            return self.send(body="<h1>Profile</h1><p>Role: user</p>", headers={"Set-Cookie": "role=dXNlcg==; Path=/; SameSite=Lax"})
        if CHALLENGE == "w3":
            return self.send(body="<h1>Staff login</h1><form method=post><input name=username><input name=password type=password><button>Log in</button></form>")
        if CHALLENGE == "w4":
            if path == "/robots.txt": return self.send(body="User-agent: *\nDisallow: /archive/\n", content_type="text/plain")
            if path == "/archive/": return self.send(body=f"<h1>Archived migration note</h1><p>{FLAG}</p>")
            return self.send(body="<h1>New portal</h1><p>The old site has been retired.</p>")
        if CHALLENGE == "w5":
            # HTML comment containing the flag
            return self.send(body=f"<h1>Inspect Me</h1><p>Look around the source.</p><!-- flag: {FLAG} -->")
        if CHALLENGE == "w6":
            # Flag shown when debug parameter is present
            if "debug=true" in self.path:
                return self.send(body=f"<h1>Secret Revealed</h1><p>{FLAG}</p>")
            return self.send(body="<h1>Parameter Needed</h1><p>Add ?debug=true to see something.</p>")
        if CHALLENGE == "w7":
            # Serve a page with JavaScript that reveals the flag
            js = f"<script>let flag = '{FLAG}'; console.log('Flag is', flag); document.getElementById('flag').innerText = flag;</script>"
            return self.send(body=f"<h1>Case Sensitive</h1><p id='flag'>???</p>{js}")
        return self.send(404, "not found")
    def do_POST(self):
        if CHALLENGE != "w3": return self.send(405, "method not allowed")
        length = int(self.headers.get("Content-Length", "0")); data = self.rfile.read(length).decode(errors="replace")
        # Deliberately models the observable result of a weak query; no database and no code execution.
        if "admin%27" in data and ("--" in data or "%23" in data): return self.send(body=f"<h1>Welcome admin</h1><p>{FLAG}</p>")
        return self.send(401, "<p>Invalid credentials</p>")
    def log_message(self, *_): pass

def main():
    HTTPServer(("0.0.0.0", 8080), App).serve_forever()

if __name__ == "__main__":
    main()
