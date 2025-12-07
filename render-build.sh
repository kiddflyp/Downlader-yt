#!/usr/bin/env bash
# Salir si hay errores
set -o errexit

# 1. Instalar librerías de Python
pip install -r requirements.txt

# 2. Descargar FFmpeg para Linux si no existe
if [ ! -f ffmpeg ]; then
    echo "Descargando FFmpeg para Linux..."
    curl -L https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -o ffmpeg.tar.xz
    
    # Extraer
    tar -xf ffmpeg.tar.xz --wildcards '*/bin/ffmpeg' '*/bin/ffprobe' --strip-components=2
    
    # Limpiar y dar permisos
    rm ffmpeg.tar.xz
    chmod +x ffmpeg ffprobe
fi
