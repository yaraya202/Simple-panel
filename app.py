from flask import Flask, request, jsonify
import os
import subprocess
import tempfile
import json

app = Flask(__name__)

API_KEY = os.environ.get("MY_API_KEY", "supersecretapikey123")
OWNER = os.environ.get("API_OWNER", "KashifRaza")

def check_api_key(req):
    key = req.headers.get("x-api-key") or req.args.get("api_key")
    return key == API_KEY

@app.route("/<owner>/download", methods=["GET"])
def download(owner):
    if owner != OWNER:
        return jsonify({"error":"Invalid owner"}), 403
    if not check_api_key(request):
        return jsonify({"error":"Unauthorized"}), 401

    url = request.args.get("url")
    typ = request.args.get("type","video")

    if not url:
        return jsonify({"error":"No URL provided"}), 400

    tmpdir = tempfile.mkdtemp()
    out_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

    try:
        # Use yt-dlp to get info JSON
        info_cmd = ["yt-dlp", "--dump-json", url]
        result = subprocess.run(info_cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)

        # Get video title and thumbnail
        title = info.get("title", "video")
        thumbnail_url = info.get("thumbnail")

        # Construct direct download URL
        if typ.lower() == "audio":
            # yt-dlp direct extraction format
            download_cmd = f"https://www.youtube.com/watch?v={info.get('id')}"
        else:
            download_cmd = f"https://www.youtube.com/watch?v={info.get('id')}"

        return jsonify({
            "title": title,
            "type": typ,
            "download_url": download_cmd,
            "thumbnail_url": thumbnail_url
        })

    except Exception as e:
        return jsonify({"error":"Failed to fetch info", "detail": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
