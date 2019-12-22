# Installation

```bash
# install dependencies
sudo apt install python3-pip uwsgi uwsgi-plugin-python mongodb
sudo pip3 install pyw scapy pymongo flask

# download repository
git clone https://github.com/pecheur/wifinet.git /tmp/wifinet

# install
sudo cp -R /tmp/wifinet /opt/wifinet
sudo cp /opt/wifinet/website/website.service /etc/systemd/system/wifinet-website.service
sudo cp /opt/wifinet/wifi/wifi@.service /etc/systemd/system/wifinet-wifi@.service

# enable services
sudo systemctl enable --now mongodb
sudo systemctl enable --now wifinet-website.service
sudo systemctl enable --now wifinet-wifi@wlan1.service
```

The website runs on port 80.

# Hardware
* Raspberry Pi 3 (Debian Buster)
* Alfa AWUS036NH
* 9dBi Antenna
