FROM openjdk:8-slim

ARG DICOOGLE_VERSION=3.0.7

LABEL MAINTAINER="Azuka Okuleye<azuka@zahymaka.com>"

WORKDIR /tmp

RUN apt-get update && apt-get install -y wget unzip

RUN wget https://github.com/bioinformatics-ua/dicoogle/releases/download/${DICOOGLE_VERSION}/Dicoogle_v${DICOOGLE_VERSION}.zip && \
    mkdir -p /dicoogle/Plugins && \
    unzip -j -o Dicoogle_v${DICOOGLE_VERSION}.zip -d /dicoogle

WORKDIR /dicoogle

CMD ["java", "-jar", "dicoogle.jar", "-s"]
