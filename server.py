import json
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ALLOWED = {
    "dQw4w9WgXcQ",
    "fABIBm5OEj4",
    "q5xl4Zip1fQ",
    "j0lSpNtjPM8",
    "TEGBZJJwgv0",
}

PLAYER_KEY = "AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w"


def stream_url(video_id):
    body = {
        "videoId": video_id,
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "20.10.38",
                "androidSdkVersion": 30,
                "hl": "es",
                "gl": "US",
            }
        },
    }
    request = urllib.request.Request(
        "https://www.youtube.com/youtubei/v1/player?prettyPrint=false&key=" + PLAYER_KEY,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "com.google.android.youtube/20.10.38 (Linux; U; Android 11) gzip",
        },
    )
    data = json.loads(urllib.request.urlopen(request, timeout=20).read())
    formats = (data.get("streamingData") or {}).get("formats") or []
    for item in formats:
        url = item.get("url")
        if url:
            return url
    raise RuntimeError("sin archivo")


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/play":
            return super().do_GET()

        video_id = (parse_qs(parsed.query).get("id") or [""])[0]
        if video_id not in ALLOWED:
            self.send_error(404)
            return
        try:
            payload = json.dumps({"url": stream_url(video_id)}).encode()
        except Exception:
            self.send_error(502)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
