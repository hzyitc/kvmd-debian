# kvmd-debian

PiKVM on Debian, Ubuntu or Armbian

## How to use

```bash
# TAG=$(curl "https://api.github.com/repos/hzyitc/kvmd-debian/releases/latest" | jq -r .tag_name)
TAG=debian-v3.134
VERSION=$(echo "$TAG" | grep -oE '[0-9]+([\.-][0-9]+)+')

# Donwload the packages
curl -L -O "https://github.com/hzyitc/kvmd-debian/releases/download/${TAG}/{python3-kvmd_${VERSION}_all.deb,kvmd-platform-v2-hdmiusb-generic_${VERSION}_all.deb}"

# Install them
dpkg -i python3-kvmd_${VERSION}_all.deb
dpkg -i kvmd-platform-v2-hdmiusb-generic_${VERSION}_all.deb
apt install --fix-broken --yes

# Prepare MSD storage
# a. Use a new partition to storage
#	mkfs.ext4 /dev/sdX
#	echo "LABEL=PIMSD  /var/lib/kvmd/msd  ext4  defaults,X-kvmd.otgmsd-user=kvmd  0  0" >> /etc/fstab
#	mount -a
#	mkdir -p /var/lib/kvmd/msd/{images,meta}
#	chown kvmd -R /var/lib/kvmd/msd/
# b. Storage in root partititon
sed -i -E 's/^([ \t]*)main\(\)$/\1#main()\n\1pass/' /usr/bin/kvmd-helper-otgmsd-remount
mkdir -p /var/lib/kvmd/msd/{images,meta}
chown kvmd -R /var/lib/kvmd/msd/

# Disable nginx to free http and https port
systemctl disable nginx

# Enable kvmd services
systemctl enable kvmd-otg kvmd-nginx kvmd

# Reboot and enjoy
reboot
```
