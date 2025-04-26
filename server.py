#!/usr/bin/env python3
import socket
import threading
import time
import sys
import platform  # İşletim sistemi kontrolü için

class Server:
    def __init__(self, host='0.0.0.0', port=54321):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {client_socket: last_heartbeat_time}
        self.running = True
        self.lock = threading.Lock()  # Thread güvenliği için kilit

    def start(self):
        """Sunucuyu başlat"""
        try:
            self._create_server_socket()
            self._print_network_info()

            # Heartbeat kontrol thread'ini başlat
            heartbeat_thread = threading.Thread(target=self._check_heartbeats, daemon=True)
            heartbeat_thread.start()

            self._accept_connections()

        except Exception as e:
            print(f"Sunucu başlatma hatası: {e}")
            sys.exit(1)
        finally:
            self._cleanup()

    def _create_server_socket(self):
        """Sunucu soketini oluştur"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Temel soket ayarları
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Sadece Linux ortamında SO_REUSEPORT uygula
            if platform.system() == "Linux":
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

            print(f"\nSunucu {self.host}:{self.port} adresinde başlatılıyor...")
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"[BAŞARILI] Sunucu {self.port} portunda dinlemede!")

        except Exception as e:
            print(f"\n[KRİTİK HATA] Sunucu başlatılamadı: {e}")
            raise

    def _print_network_info(self):
        """Ağ bilgilerini göster"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"\nSunucu Bilgileri:")
            print(f"- Hostname: {hostname}")
            print(f"- Yerel IP: {local_ip}")
            print(f"- Dinlenen Port: {self.port}")
        except Exception as e:
            print(f"Ağ bilgileri alınamadı: {e}")

    def _accept_connections(self):
        """İstemci bağlantılarını kabul et"""
        print("\nBağlantılar bekleniyor...")
        try:
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()

                    # İstemciyi kaydet ve thread başlat
                    with self.lock:
                        self.clients[client_socket] = time.time()

                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()

                    print(f"\nYeni bağlantı: {client_address}")
                    print(f"Aktif bağlantı sayısı: {len(self.clients)}")

                except OSError as e:
                    if self.running:
                        print(f"Bağlantı kabul hatası: {e}")
                    continue

        except KeyboardInterrupt:
            print("\nSunucu kapatılıyor...")
        finally:
            self.running = False

    def _handle_client(self, client_socket, client_address):
        """İstemci bağlantısını yönet"""
        try:
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        raise ConnectionError("Bağlantı koptu")

                    if data.decode().strip() == "ping":
                        with self.lock:
                            self.clients[client_socket] = time.time()
                        client_socket.sendall(b"pong")
                    else:
                        print(f"{client_address} >> {data.decode()}")

                except (ConnectionError, ConnectionResetError):
                    break
                except Exception as e:
                    print(f"İstemci işleme hatası: {e}")
                    break

        finally:
            self._remove_client(client_socket, client_address)

    def _check_heartbeats(self):
        """Bağlantıları kontrol et (heartbeat kontrolü)"""
        while self.running:
            current_time = time.time()
            dead_clients = []

            # Bağlantı kontrolünü thread-safe şekilde yap
            with self.lock:
                for client_socket, last_heartbeat in list(self.clients.items()):
                    if current_time - last_heartbeat > 10:
                        print(f"\nHeartbeat alınamadı: {client_socket.getpeername()}")
                        dead_clients.append(client_socket)

            # Tespit edilen ölü bağlantıları kaldır
            for client_socket in dead_clients:
                self._remove_client(client_socket)

            time.sleep(1)

    def _remove_client(self, client_socket, client_address=None):
        """İstemciyi listeden güvenli şekilde çıkar (thread-safe)"""
        with self.lock:
            if client_socket in self.clients:
                addr = client_address or client_socket.getpeername()
                print(f"\nİstemci ayrıldı: {addr}")
                try:
                    client_socket.close()
                except Exception:
                    pass
                del self.clients[client_socket]
                print(f"Kalan bağlantı sayısı: {len(self.clients)}")
            else:
                # Eğer zaten silinmişse sadece güvenli şekilde soketi kapat
                try:
                    client_socket.close()
                except Exception:
                    pass

    def _cleanup(self):
        """Temizlik yap"""
        print("\nTüm bağlantılar kapatılıyor...")
        with self.lock:
            for client_socket in list(self.clients.keys()):
                self._remove_client(client_socket)
        if self.server_socket:
            self.server_socket.close()
        print("Sunucu kapatıldı.")

if __name__ == "__main__":
    print("Linux/Windows Socket Sunucusu v0.1")
    server = Server()
    server.start()
