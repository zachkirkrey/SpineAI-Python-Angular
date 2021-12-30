#!/bin/bash

(cd "${0%/*}" && docker run --network host -p 4242:4242 -p 8042:8042 --rm -v $(pwd)/orthanc-plugins-docker/db:/var/lib/orthanc/db -v $(pwd)/orthanc-plugins-docker.json:/etc/orthanc/orthanc.json:ro jodogne/orthanc-plugins:1.9.7)
