#!/usr/bin/env python3
import socket
import threading
import time
import sys

class Server:
    def __init__(self, host='0.0.0.0', port=54321):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {client_socket: last_heartbeat_time}
        self.running = True
        
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
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                    
                    mesaj = data.decode().strip()
                    
                    if mesaj == "ping":
                        self.clients[client_socket] = time.time()
                        client_socket.sendall(b"pong")  # 🔥 Burayı ekledik: cevap olarak "pong" gönder
                    else:
                        print(f"{client_address} >> {mesaj}")
                        
                except (ConnectionError, ConnectionResetError) as e:
                    break
                except Exception as e:
                    print(f"İstemci işleme hatası: {e}")
                    break
                    
        finally:
            self._remove_client(client_socket, client_address)
    
    def _check_heartbeats(self):
        """Bağlantıları kontrol et"""
        while self.running:
            current_time = time.time()
            for client_socket, last_heartbeat in list(self.clients.items()):
                if current_time - last_heartbeat > 10:
                    print(f"\nHeartbeat alınamadı: {client_socket.getpeername()}")
                    self._remove_client(client_socket)
            time.sleep(1)
    
    def _remove_client(self, client_socket, client_address=None):
        """İstemciyi listeden çıkar"""
        if client_socket in self.clients:
            addr = client_address or client_socket.getpeername()
            print(f"\nİstemci ayrıldı: {addr}")
            client_socket.close()
            del self.clients[client_socket]
            print(f"Kalan bağlantı sayısı: {len(self.clients)}")
    
    def _cleanup(self):
        """Temizlik yap"""
        print("\nTüm bağlantılar kapatılıyor...")
        for client_socket in list(self.clients.keys()):
            self._remove_client(client_socket)
        if self.server_socket:
            self.server_socket.close()
        print("Sunucu kapatıldı.")

if __name__ == "__main__":
    print("Linux Socket Sunucusu v2.0")
    server = Server()
    server.start()
