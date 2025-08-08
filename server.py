from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Pasta temporária para músicas
TEMP_DIR = "cache"
os.makedirs(TEMP_DIR, exist_ok=True)

# HTML com estilo tipo Spotify
HTML_HOME = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Spotify Particular</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: white;
            text-align: center;
            padding: 20px;
        }
        input[type=text] {
            padding: 10px;
            width: 70%;
            border: none;
            border-radius: 20px;
            font-size: 16px;
        }
        input[type=submit] {
            padding: 10px 20px;
            background: #1DB954;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
        }
        audio {
            margin-top: 20px;
            width: 100%;
        }
    </style>
</head>
<body>
    <h1>🎵 Spotify Particular</h1>
    <form method="get" action="/play">
        <input type="text" name="q" placeholder="Digite o nome da música..." required>
        <input type="submit" value="Tocar">
    </form>
    {% if music_url %}
    <h2>{{ title }}</h2>
    <img src="{{ thumbnail }}" width="300"><br>
    <audio controls autoplay>
        <source src="{{ music_url }}" type="audio/mp4">
        Seu navegador não suporta áudio.
    </audio>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_HOME)

@app.route("/play")
def play():
    query = request.args.get("q")
    if not query:
        return render_template_string(HTML_HOME)

    # Nome temporário
    filename = f"{uuid.uuid4()}.m4a"
    filepath = os.path.join(TEMP_DIR, filename)

    # Opções yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': filepath,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'default_search': 'ytsearch1'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)

    title = info.get('title', 'Música')
    thumbnail = info.get('thumbnail', '')
    music_url = f"/stream/{filename}"

    return render_template_string(HTML_HOME, music_url=music_url, title=title, thumbnail=thumbnail)

@app.route("/stream/<filename>")
def stream(filename):
    filepath = os.path.join(TEMP_DIR, filename)
    return send_file(filepath, mimetype="audio/mp4")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
