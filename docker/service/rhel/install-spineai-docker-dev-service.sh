#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

cd "$(dirname "$0")"
cp spineai-docker-dev.service /etc/systemd/system/spineai-docker-dev.service
cp spineai-docker-dev-update.service /etc/systemd/system/spineai-docker-dev-update.service
systemctl enable spineai-docker-dev
systemctl enable spineai-docker-dev-update
