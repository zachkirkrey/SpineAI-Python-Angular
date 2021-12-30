FROM ubuntu:18.04

MAINTAINER Billy Cao <billy@spineai.com>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq && apt-get install -qqy \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    lxc \
    iptables

RUN curl -sSL https://get.docker.com/ | sh

# Install nvidia drivers.
RUN add-apt-repository -y ppa:graphics-drivers/ppa
RUN apt-get update -qq && apt-get install -qqy nvidia-driver-440

# Install nvidia-docker
RUN curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
RUN curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu18.04/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
RUN apt-get update -qq && apt-get install -qqy nvidia-container-toolkit

ADD ./wrapdocker /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker

VOLUME /var/lib/docker
ENV PORT 2375
CMD ["wrapdocker"]
