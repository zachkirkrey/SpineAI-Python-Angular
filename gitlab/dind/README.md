# Docker-in-docker with nvidia-docker

This provides a dind image for running GPU accelerated containers.

This image is similar to the official dind image, except:

- Based on Ubuntu instead of Alpine linux.
- Installs NVIDIA drivers.
- Installs nvidia-docker. (enables --gpus=all)

## Table of Contents

- [Usage](#usage)

## Usage

```sh
docker run --it --name dind spineai/nvidia-dind
docker run --it --link dind my-container
```
