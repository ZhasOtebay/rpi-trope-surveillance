#!/usr/bin/env python3
import cv2
import subprocess
import logging
import time
import os

# ===================== НАСТРОЙКИ =====================
CAMERA_IP = "192.168.1.100"
CAMERA_USER = "admin"
CAMERA_PASSWORD = "B078AD7B" 
CAMERA_STREAM = "main"  # или "sub" для субпотока

RTSP_URL = f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/{CAMERA_STREAM}"
FFMPEG_SERVER = "rtmp://100.26.111.7:1935/live/stream1"
FRAME_RATE = 15
RESOLUTION = (1280, 720)  # Подберите под вашу камеру

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

def test_rtsp_connection():
    """Проверяем доступность RTSP потока"""
    try:
        logger.info(f"Testing RTSP connection to {RTSP_URL}")
        cap = cv2.VideoCapture(RTSP_URL)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                logger.info("RTSP connection successful!")
                return True
            else:
                logger.warning("RTSP connected but no frames")
                return False
        else:
            logger.error("Cannot open RTSP stream")
            return False
    except Exception as e:
        logger.error(f"RTSP test failed: {e}")
        return False

def start_ffmpeg(width, height, fps, server_url):
    """Запускаем FFmpeg для стриминга с оптимизацией для сети"""
    command = [
        "ffmpeg",
        "-y", "-an",
        "-rtsp_transport", "tcp",  # Используем TCP для стабильности
        "-i", RTSP_URL,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-b:v", "500k",  # Низкий битрейт для Wi-Fi
        "-maxrate", "500k",
        "-bufsize", "1000k",
        "-pix_fmt", "yuv420p",
        "-f", "flv",
        server_url
    ]
    logger.info(f"FFmpeg command: {' '.join(command)}")
    return subprocess.Popen(command)

def test_ffmpeg():
    """Проверяем доступность FFmpeg"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("FFmpeg is available")
            return True
        else:
            logger.error("FFmpeg not working")
            return False
    except Exception as e:
        logger.error(f"FFmpeg test failed: {e}")
        return False

def check_network():
    """Проверяем сетевое подключение"""
    try:
        # Проверяем связь с камерой
        result = subprocess.run(["ping", "-c", "1", "-W", "2", CAMERA_IP],
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Camera {CAMERA_IP} is reachable")
        else:
            logger.warning(f"Camera {CAMERA_IP} not reachable")
        
        # Проверяем интернет (AWS)
        result = subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Internet connection OK")
        else:
            logger.warning("No internet connection")
            
    except Exception as e:
        logger.error(f"Network check failed: {e}")

def main():
    logger.info("Starting RTSP to RTMP streamer")
    
    # Проверяем сеть
    check_network()
    
    # Проверяем FFmpeg
    if not test_ffmpeg():
        logger.error("FFmpeg not available")
        return

    # Проверяем RTSP подключение
    if not test_rtsp_connection():
        logger.error("RTSP connection failed")
        logger.info("Please check:")
        logger.info("1. Camera credentials")
        logger.info("2. Network connection to camera")
        logger.info("3. RTSP URL format")
        return

    # Запускаем FFmpeg напрямую (более стабильно)
    try:
        logger.info("Starting FFmpeg stream...")
        ffmpeg_proc = start_ffmpeg(RESOLUTION[0], RESOLUTION[1], FRAME_RATE, FFMPEG_SERVER)
        
        # Мониторим процесс
        start_time = time.time()
        while True:
            # Проверяем статус процесса
            if ffmpeg_proc.poll() is not None:
                logger.error("FFmpeg process stopped, restarting...")
                ffmpeg_proc = start_ffmpeg(RESOLUTION[0], RESOLUTION[1], FRAME_RATE, FFMPEG_SERVER)
            
            # Логируем каждые 30 секунд
            if time.time() - start_time > 30:
                logger.info("Stream is running...")
                start_time = time.time()
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    
    except Exception as e:
        logger.error(f"Stream error: {e}")
    
    finally:
        if 'ffmpeg_proc' in locals():
            ffmpeg_proc.terminate()
            logger.info("FFmpeg stopped")

if __name__ == "__main__":
    main()
