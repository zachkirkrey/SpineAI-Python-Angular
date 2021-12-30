#!/bin/bash

cat /opt/spineai/spineai/docker/docker-password.txt | docker login --username spineaibilly --password-stdin
docker pull spineai/spineai-frontend:latest
docker pull spineai/spineai-api:latest
docker pull spineai/spineai-backend:latest
docker image prune -f
exit 0
