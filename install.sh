#!/bin/bash
set -e

if [ ! -z $1 ]; then
    IMAGE_FILE="$1"
fi    

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 
fi

if [ ! -z $IMAGE_FILE ]; then
    if [ ! $(which qemu-arm-static) ]; then
	echo "qemu-arm-static is not installed. Please run 'apt install qemu-arm-static'"
	exit
    elif [ ! $(which systemd-nspawn) ]; then
	echo "systemd-container is not installed. Please run 'apt install systemd-container'"
	exit
    fi
fi

function cleanup {
    echo "unmount"
    rm -rf $DEST/usr/bin/qemu-arm-static
    if [ -f $DEST/etc/ld.so.preload.backup ]; then
	mv $DEST/etc/ld.so.preload.backup $DEST/etc/lds.so.preload
    fi
    umount $DEST/dev/pts    
    umount $DEST/sys/
    umount $DEST/proc/    
    umount ${DEST}/boot/
    umount ${DEST}
    rmdir ${DEST}
    losetup -d ${LOOP}
}

if [ ! -z $IMAGE_FILE ]; then
    DEST=$(mktemp -d)    
    echo "mount $IMAGE_FILE at $DEST"
    LOOP=$(sudo losetup --show -fP "${IMAGE_FILE}")
    mount ${LOOP}p2 $DEST
    mount ${LOOP}p1 $DEST/boot/

    mount --bind /sys $DEST/sys/
    mount --bind /proc $DEST/proc/
    mount --bind /dev/pts $DEST/dev/pts
    cp $(which qemu-arm-static) $DEST/usr/bin
    if [ -f $DEST/etc/ld.so.preload ]; then
	mv -f $DEST/etc/ld.so.preload $DEST/etc/lds.so.preload.backup
    fi
    trap cleanup EXIT
else
    DEST=/  # root directory
fi


# copy files
mkdir -p $DEST/opt/wifinet
cp -R ./{website,wifi,requirements.txt} $DEST/opt/wifinet/
cp ./website/website.service $DEST/etc/systemd/system/wifinet-website.service
cp ./wifi/wifi@.service $DEST/etc/systemd/system/wifinet-wifi@.service


if [ ! -z $IMAGE_FILE ]; then
cat << EOF | systemd-nspawn -D $DEST /bin/bash
apt update
apt install -y python3-pip uwsgi uwsgi-plugin-python mongodb
pip3 install -r /opt/wifinet/requirements.txt
systemctl enable mongodb
systemctl enable wifinet-website.service
systemctl enable wifinet-wifi@wlan1.service
EOF
else
    apt update
    apt install -y python3-pip uwsgi uwsgi-plugin-python mongodb
    pip3 install -r /opt/wifinet/requirements.txt
    systemctl enable --now mongodb
    systemctl enable --now wifinet-website.service
    systemctl enable --now wifinet-wifi@wlan1.service
fi
