# **📡 Python TCP Socket Client \+ Server \+ Heartbeat \+ Timeout**

## **🧾 Proje Hakkında (About the Project)**

Bu proje, Python ile geliştirilmiş kurumsal düzeyde bir **TCP istemci ve sunucu (Socket Client \+ Server)** uygulamasıdır. İstemci ile sunucu arasında bir heartbeat (nabız atışı) dinleme mekanizması vardır.  İstemci, sunucuya bağlanarak "ping" mesajları gönderir ve sunucudan gelen "pong" cevaplarını dinleyerek bağlantının hala devam edip etmediğini kontrol eder. Sunucu ise gelen bağlantıları kabul eder, "ping" mesajlarına yanıt verir ve istemcilerin bağlantı sürekliliğini izler.

This project is a production-ready **Python TCP Socket Client \+ Server** system. The client connects to the server, sends periodic `ping` messages, and expects `pong` replies. The server accepts client connections, responds to pings, and monitors connection health.

---

## **✨ Özellikler (Features)**

* Ping-pong protokolü ile bağlantı sağlığı kontrolü / Connection health monitoring via ping-pong protocol  
* Sunucuda istemcilerin kalp atışı takibi / Heartbeat monitoring on server side  
* Belirli süre boyunca pong gelmezse zaman aşımı kontrolü / Timeout detection if no pong response  
* Bağlantı koptuğunda istemcide otomatik yeniden bağlanma / Automatic client reconnect after disconnection  
* İsteğe bağlı sınırsız bağlantı denemesi / Optional unlimited reconnect attempts  
* Yalnızca hata durumlarını log dosyasına yazma / Logging only error events to file  
* Terminal görünümüyle okunabilir bilgi akışı / Clean terminal output for monitoring  
* Geliştirici dostu, yorum satırlı Python kodu / Developer-friendly and well-commented Python code

---

## **🔧 Nasıl Kullanılır? (How to Use)**

### **1\. Gereksinimler (Requirements)**

Python 3.7+

### **2\. Bağlantı Ayarlarını Yapılandırın (Configure)**

#### **İstemci için (Client Configuration):**

`client.py` içindeki `ClientConfig` alanını kendi sunucunuza göre düzenleyin:
```
config = ClientConfig(  
    host="192.168.1.107",         # Sunucu IP adresi / Server IP  
    port=54321,                   # Sunucu portu / Server port  
    reconnect_attempts=0,        # 0 = sınırsız yeniden deneme / 0 = unlimited retry  
    heartbeat_interval=2,        # Ping gönderme aralığı / Ping interval (seconds)  
    receive\_timeout=3,           # Veri bekleme zaman aşımı / Receive timeout (seconds)  
    pong_timeout=5,              # Pong alınmazsa kopar / Pong timeout (seconds)  
    log_file="client.log"        # Hataların loglanacağı dosya / Error log file  
)
```
#### **Sunucu için (Server Configuration):**

`server.py` içindeki varsayılan ayarlar:
```
host = '0.0.0.0'  # Tüm ağ arayüzlerinden bağlantı kabul eder / Accept connections from all interfaces  
port = 54321      # Dinlenecek port / Listening port  
heartbeat_timeout = 10  \# 10 saniye ping alınmazsa bağlantı kesilir / Disconnect if no ping for 10 seconds
```
### **3\. Çalıştır (Run)**

#### **Sunucuyu başlat (Start the Server):**

python3 server.py

#### **İstemciyi başlat (Start the Client):**

python3 client.py  
---

## **⚡ Parametreler (Configuration Parameters)**

### **İstemci (Client):**

| Parametre | Açıklama | Description |
| ----- | ----- | ----- |
| `host` | Sunucu IP adresi | Server IP address |
| `port` | Bağlantı portu | Server port |
| `reconnect_attempts` | 0 verilirse sınırsız deneme | 0 \= unlimited retry attempts |
| `heartbeat_interval` | Ping gönderme süresi (sn) | Interval between pings (in seconds) |
| `receive_timeout` | Veri bekleme süre limiti | Timeout for receiving data (in seconds) |
| `pong_timeout` | Pong gelmezse bağlantıyı kopar | Disconnect if pong is not received |
| `log_file` | Sadece hataların yazılacağı dosya | File for logging only errors |

### **Sunucu (Server):**

| Parametre | Açıklama (TR) | Description (EN) |
| :---- | :---- | :---- |
| `host` | Dinleme IP adresi (genellikle '0.0.0.0') | Listening IP address (usually '0.0.0.0') |
| `port` | Dinlenecek TCP portu | TCP port to listen for incoming connections |
| `heartbeat_timeout` | Belirli sürede ping alınmazsa bağlantıyı kesme süresi | Timeout duration if no ping is received |

---

## **🌐 Uluslararası Kullanım (Internationalization)**

Bu README dosyası hem Türkçe hem İngilizce açıklamalar içermektedir.  
This README contains both Turkish and English explanations for accessibility.

---

## **✅ Katkı (Contributing)**

Bu projeyi geliştirmek istiyorsanız, lütfen önce bir `issue` oluşturun veya `pull request` gönderin.  
If you want to contribute, feel free to open an issue or submit a pull request.

---

## **© Lisans (License)**

MIT Lisansı (MIT License)  
Bu proje MIT lisansı altındadır. İstediğiniz gibi kullanabilir, değiştirebilir ve dağıtabilirsiniz.  
This project is licensed under the MIT License. You are free to use, modify, and distribute it.

---

## **🚀 Projeyi Klonla (Clone the Project)**

git clone https://github.com/ofarukuyduran/heartbeat-based-tcp-server-client.git

