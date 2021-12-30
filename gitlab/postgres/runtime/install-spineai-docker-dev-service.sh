#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

cd "$(dirname "$0")"
cp spineai-postgres-gitlab-dev.service /etc/systemd/system/spineai-postgres-gitlab-dev.service
systemctl enable spineai-postgres-gitlab-dev
