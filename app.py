from flask import Flask, request, jsonify, send_file
import os, subprocess, tempfile

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
    out_template = tmpdir + "/%(title)s.%(ext)s"

    if typ.lower() == "audio":
        cmd = ["yt-dlp","-x","--audio-format","mp3","-o", out_template, url]
    else:
        cmd = ["yt-dlp","-f","bestvideo+bestaudio/best","-o", out_template, url]

    try:
        subprocess.check_call(cmd)
        files = [f for f in os.listdir(tmpdir) if not f.startswith(".")]
        if not files:
            return jsonify({"error":"Download failed"}), 500
        filepath = tmpdir + "/" + files[0]
        return send_file(filepath, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error":"Download error","detail":str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
