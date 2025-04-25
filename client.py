# client.py

#!/usr/bin/env python3
import socket
import threading
import time
import os
from dataclasses import dataclass

# === YAPILANDIRMA SINIFI ===

@dataclass
class ClientConfig:
    """İstemci yapılandırma ayarları (GUI entegrasyonu için uygun)"""
    host: str = '127.0.0.1'
    port: int = 54321
    reconnect_attempts: int = 0  # 0 verilirse sınırsız bağlantı denemesi
    heartbeat_interval: int = 2  # Ping gönderme aralığı (saniye)
    receive_timeout: int = 5     # Veri alma timeout süresi (saniye)
    pong_timeout: int = 5        # Pong alınmazsa bağlantı kopma süresi (saniye)
    log_file: str = "client.log" # Sadece hata loglarının yazılacağı dosya

# === LOG SİSTEMİ ===

class Logger:
    """
    Ekrana bilgi + sadece hata/kritik durumları dosyaya yazan sistem.
    Gereksiz log birikimini önler.
    """
    def __init__(self, log_file):
        self.log_file = log_file
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(log_file), exist_ok=True) if '/' in log_file else None

    def log_info(self, message):
        """Sadece ekrana yazılır (bilgilendirme mesajları)"""
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        print(f"{timestamp} {message}")

    def log_error(self, message):
        """Ekrana yazılır + log dosyasına yazılır (hata mesajları)"""
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        full_message = f"{timestamp} {message}"
        print(full_message)
        with self._lock:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(full_message + '\n')

# === ANA TCP İSTEMCİ SINIFI ===

class SocketClient:
    """Sunucuya bağlanan, ping-pong ile bağlantıyı kontrol eden TCP istemcisi"""
    def __init__(self, config: ClientConfig):
        self.config = config
        self.socket = None
        self.running = threading.Event()
        self.heartbeat_active = threading.Event()
        self.logger = Logger(config.log_file)
        self.reconnect_count = 0
        self.last_pong_time = time.time()

    def start(self):
        """İstemciyi başlatır, bağlantı koparsa yeniden dener"""
        self.logger.log_info("Socket Client başlatılıyor...")
        self.running.set()
        while self.running.is_set():
            if not self._connect():
                self.reconnect_count += 1
                # 0 ise sınırsız deneme yap
                if self.config.reconnect_attempts > 0 and self.reconnect_count > self.config.reconnect_attempts:
                    self.logger.log_error(f"[HATA] Maksimum yeniden bağlanma denemesi ({self.config.reconnect_attempts}) aşıldı. İstemci duruyor.")
                    break
                time.sleep(2)
                continue

            self.reconnect_count = 0
            self.heartbeat_active.set()
            threading.Thread(target=self._send_heartbeat, daemon=True).start()
            threading.Thread(target=self._check_pong_timeout, daemon=True).start()
            self._handle_receive()

    def stop(self):
        """İstemciyi düzgün şekilde kapatır"""
        self.logger.log_info("İstemci durduruluyor...")
        self.running.clear()
        self.heartbeat_active.clear()
        self._disconnect()

    def _connect(self):
        """Sunucuya bağlanmaya çalışır"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.receive_timeout)
            self.logger.log_info(f"{self.config.host}:{self.config.port} adresine bağlanılıyor...")
            self.socket.connect((self.config.host, self.config.port))

            # TCP keepalive aktif et
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            try:
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5)
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2)
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
            except AttributeError:
                pass  # Windows sistemlerde bu opsiyonlar olmayabilir

            self.logger.log_info("[BAĞLANTI] Sunucuya başarıyla bağlandı.")
            self.last_pong_time = time.time()
            return True
        except Exception as e:
            self.logger.log_error(f"[BAĞLANTI HATASI] {e}")
            self._disconnect()
            return False

    def _disconnect(self):
        """Bağlantıyı keser ve soketi kapatır"""
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        self.socket = None
        self.logger.log_info("[BAĞLANTI] Bağlantı kesildi.")

    def _send_heartbeat(self):
        """Sunucuya periyodik ping gönderir (pong cevabını ayrı thread alır)"""
        while self.running.is_set() and self.heartbeat_active.is_set():
            try:
                if self.socket:
                    self.socket.settimeout(3)
                    self.socket.sendall(b"ping")
                    self.socket.settimeout(self.config.receive_timeout)
                time.sleep(self.config.heartbeat_interval)
            except (socket.timeout, socket.error, OSError) as e:
                self.logger.log_error(f"[HEARTBEAT HATASI] {e}")
                self._disconnect()
                break

    def _handle_receive(self):
        """Sunucudan gelen verileri okur"""
        try:
            while self.running.is_set():
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        raise ConnectionError("Sunucu bağlantıyı kapattı")

                    message = data.decode(errors='ignore').strip()
                    if message == "pong":
                        self.last_pong_time = time.time()  # Son başarılı cevap zamanı
                        continue

                    self.logger.log_info(f"[SUNUCUDAN] {message}")

                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.log_error(f"[VERİ ALMA HATASI] {e}")
                    break
        finally:
            self.heartbeat_active.clear()
            self._disconnect()

    def _check_pong_timeout(self):
        """Belirli süre boyunca pong alınmazsa bağlantıyı koparır"""
        while self.running.is_set() and self.heartbeat_active.is_set():
            if time.time() - self.last_pong_time > self.config.pong_timeout:
                self.logger.log_error("[ZAMAN AŞIMI] Sunucudan pong cevabı alınamadı. Bağlantı kopartılıyor.")
                self._disconnect()
                break
            time.sleep(1)

# === ÇALIŞTIRICI ===

if __name__ == "__main__":
    config = ClientConfig(
        host="192.168.1.105",
        port=54321,
        reconnect_attempts=0,  # 0 → sınırsız deneme
        heartbeat_interval=2,
        receive_timeout=3,
        pong_timeout=5,
        log_file="client.log"
    )
    client = SocketClient(config)
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()
