from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os
import platform # Importamos esto para detectar si es Windows o Linux

app = Flask(__name__)

# Definir ruta base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    # Recibir calidad del usuario (128, 192, 320)
    quality = request.form.get('quality', '192')

    if not video_url:
        return "Error: No enviaste ninguna URL", 400

    try:
        # --- Lógica Inteligente de FFmpeg ---
        # Si estamos en Windows (Tu PC), forzamos a buscar el .exe en la carpeta.
        # Si estamos en la Nube (Linux/Render), dejamos que el sistema lo busque solo.
        if platform.system() == 'Windows':
            ffmpeg_loc = BASE_DIR
        else:
            ffmpeg_loc = None # En Linux se instala en el sistema global

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_loc, 
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            final_name = os.path.basename(mp3_filename)

        # Programar borrado automático
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(mp3_filename):
                    os.remove(mp3_filename)
            except Exception as error:
                print(f"Error borrando archivo: {error}")
            return response

        # Enviar archivo al usuario
        response = send_file(mp3_filename, as_attachment=True)
        response.headers["x-filename"] = final_name 
        return response

    except Exception as e:
        print(f"Error: {e}")
        return f"Ocurrió un error: {str(e)}", 500

if __name__ == '__main__':
    # 'host=0.0.0.0' hace que el servidor sea visible externamente si lo subes a la nube
    app.run(debug=True, host='0.0.0.0', port=5000)