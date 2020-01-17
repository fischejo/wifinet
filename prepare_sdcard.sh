#!/bin/bash
set -e

if [ ! -z $1 ]; then
    IMAGE_FILE="$1"
else
    echo "No raspian image set."
fi    

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 
fi

if [ ! $(which qemu-arm-static) ]; then
    echo "qemu-arm-static is not installed. Please run 'apt install qemu-arm-static'"
    exit
elif [ ! $(which systemd-nspawn) ]; then
    echo "systemd-container is not installed. Please run 'apt install systemd-container'"
    exit
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


# copy files
mkdir -p $DEST/opt/wifinet
cp -R ./{ap,website,sniffer,requirements.txt,install.sh} $DEST/opt/wifinet/
chmod +x $DEST/opt/wifinet/install.sh

# install 
systemd-nspawn -D $DEST /opt/wifinet/install.sh

