#!/bin/bash

apt update
apt install -y python3-pip uwsgi uwsgi-plugin-python3 mongodb hostapd dnsmasq
pip3 install -r /opt/wifinet/requirements.txt

SRC="$( cd "$(dirname "$0")" ; pwd -P )"
cp $SRC/ap/hostapd.conf /etc/hostapd/hostapd.conf
cp $SRC/ap/dnsmasq.conf /etc/dnsmasq.conf
cp $SRC/ap/dhcpcd.conf /etc/dhcpcd.conf
cp $SRC/website/website.service /etc/systemd/system/wifinet-website.service
cp $SRC/sniffer/sniffer@.service /etc/systemd/system/wifinet-sniffer@.service
cp $SRC/sniffer/sniffer@.timer /etc/systemd/system/wifinet-sniffer@.timer
cp $SRC/sniffer/80-monitors.rules /etc/udev/rules.d/80-monitors.rules

systemctl enable mongodb
systemctl enable wifinet-website.service
systemctl enable wifinet-sniffer@mon0.timer
systemctl enable hostapd.service
systemctl enable dnsmasq.service
