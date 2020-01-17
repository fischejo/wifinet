# Installation

```bash
# download repository
git clone https://github.com/pecheur/wifinet.git wifinet
cd wifinet
sudo mkdir -p /opt/wifinet
sudo cp -R ./{ap,website,sniffer,requirements.txt,install.sh} /opt/wifinet/
sudo /opt/wifinet/install.sh
```

# Prepare Raspian SD-Card

Only tested under Ubuntu 16.08. 

```bash
wget -O raspbian_lite_latest.img  https://downloads.raspberrypi.org/raspbian_lite_latest
sudo ./prepare_sdcard.sh raspbian_lite_latest.img
```

# Hardware

* Raspberry Pi 3 (Debian Buster)
* Alfa AWUS036NH
* 9dBi Antenna

# Access Point

An access point is started with SSID: `wifinet` and password `12345678`. The
website is reachable under `172.16.0.1`.
