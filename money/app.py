from flask import Flask, request, Response, render_template
import yt_dlp
import requests

app = Flask(__name__)

def get_best_progressive(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = [f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') != 'none']
        if not formats:
            return None
        best = max(formats, key=lambda f: f.get('height', 0))
        return {
            "quality": best.get("format_note"),
            "ext": best.get("ext"),
            "url": best.get("url"),
            "original_url": url
        }

@app.route('/')
def home():
    return render_template('index.html')

# API endpoint to fetch best progressive link
@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url:
        return {"error": "No URL provided"}, 400

    result = get_best_progressive(url)
    if result:
        return {"success": True, "data": result}
    return {"success": False, "message": "No combined video+audio stream found"}, 404

# Proxy endpoint to force download
@app.route('/download-proxy')
def download_proxy():
    video_url = request.args.get('video_url')
    if not video_url:
        return "No video URL provided", 400

    # Stream the video to client
    r = requests.get(video_url, stream=True)
    return Response(
        r.iter_content(chunk_size=1024*1024),
        content_type="video/mp4",
        headers={"Content-Disposition": "attachment; filename=shorts_video.mp4"}
    )

if __name__ == "__main__":
    app.run(debug=True)
