#!/usr/bin/env python3
import subprocess
import logging
import time
import shutil
import signal
import sys

# ===================== НАСТРОЙКИ =====================
CAMERA_IP = "192.168.1.100"
CAMERA_USER = "admin"
CAMERA_PASSWORD = "B078AD7B"
RTSP_URL = f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/main"

# Домен и RTMP
AWS_DOMAIN = "terradatalab.org"
FFMPEG_SERVER = f"rtmp://{AWS_DOMAIN}:1935/live/stream"

# Интерфейсы
CAMERA_INTERFACE = "eth0"
AWS_INTERFACE = "wlan0"

# Лёгкие параметры (подходит для Pi)
FRAME_RATE = 10
RESOLUTION = "640x360"       # Маленькое разрешение = меньше нагрузка
BITRATE = "400k"             # Низкий битрейт
PRESET = "ultrafast"         # Минимальная задержка, минимальная нагрузка

# Логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("streamer")

# Для graceful shutdown
running = True

def signal_handler(signum, frame):
    global running
    logger.info("🛑 Получен сигнал завершения...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_network():
    """Проверяем сеть через публичный DNS"""
    logger.info("🔍 Проверка сети...")

    # 1. Камера
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "5", "-I", CAMERA_INTERFACE, CAMERA_IP],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10
        )
        if result.returncode != 0:
            logger.error("❌ Камера недоступна")
            return False
        logger.info("✅ Камера доступна")
    except Exception as e:
        logger.error(f"❌ Ошибка пинга камеры: {e}")
        return False

    # 2. Домен через Wi-Fi
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "5", "-I", AWS_INTERFACE, AWS_DOMAIN],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10
        )
        if result.returncode != 0:
            logger.error("❌ Домен недоступен")
            return False
        logger.info("✅ Домен доступен")
    except Exception as e:
        logger.error(f"❌ Ошибка пинга домена: {e}")
        return False

    # 3. DNS через Google
    try:
        result = subprocess.run(
            ["dig", "@8.8.8.8", AWS_DOMAIN, "+short", "+time=5"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and "34.228.167.24" in result.stdout:
            logger.info("✅ DNS: terradatalab.org → 34.228.167.24")
            return True
        else:
            logger.error("❌ DNS не разрешился в 34.228.167.24")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка DNS: {e}")
        return False

def start_ffmpeg():
    """Запускаем ffmpeg с перекодированием в H.264"""
    cmd = [
        "ffmpeg",
        "-y",                              # Перезаписывать
        "-rtsp_transport", "tcp",          # Надёжное соединение
        "-i", RTSP_URL,                    # Источник
        "-vf", f"fps={FRAME_RATE},scale={RESOLUTION}",  # Уменьшаем нагрузку
        "-c:v", "libx264",                # Кодек H.264
        "-preset", PRESET,                 # ultrafast = меньше CPU
        "-tune", "zerolatency",           # Для стрима
        "-b:v", BITRATE,                  # Битрейт
        "-g", "20",                       # GOP = 2x FPS
        "-keyint_min", "20",
        "-sc_threshold", "0",
        "-an",                             # Убираем аудио
        "-f", "flv",                       # Формат для RTMP
        FFMPEG_SERVER                      # Назначение
    ]

    logger.info("🚀 Запуск ffmpeg...")
    logger.debug(f"Команда: {' '.join(cmd)}")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        return proc
    except Exception as e:
        logger.error(f"❌ Не удалось запустить ffmpeg: {e}")
        return None

def monitor_ffmpeg(proc):
    """Читаем stderr ffmpeg"""
    while True:
        line = proc.stderr.readline()
        if not line:
            break
        line = line.strip()
        if "frame=" in line and "fps=" in line:
            logger.info(f"📊 {line}")
        elif any(kw in line.lower() for kw in ["error", "failed", "invalid"]):
            logger.error(f"❌ FFmpeg: {line}")

def main():
    logger.info("🟢 Стример запущен")
    logger.info(f"🌍 Стрим в: {FFMPEG_SERVER}")

    while running:
        if not check_network():
            time.sleep(10)
            continue

        proc = start_ffmpeg()
        if not proc:
            time.sleep(5)
            continue

        logger.info(f"mPid: {proc.pid}")

        try:
            while running:
                if proc.poll() is not None:
                    code = proc.returncode
                    logger.error(f"💥 FFmpeg завершился: {code}")
                    break
                monitor_ffmpeg(proc)
                time.sleep(0.5)

        except Exception as e:
            logger.error(f"⚠️ Ошибка: {e}")

        finally:
            if proc.poll() is None:
                logger.info("✋ Завершаем ffmpeg...")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except:
                    proc.kill()

        logger.info("🔄 Перезапуск через 5 сек...")
        time.sleep(5)

    logger.info("🔴 Завершение работы")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Остановлен пользователем")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
    finally:
        sys.exit(0)

