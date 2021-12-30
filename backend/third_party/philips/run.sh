#!/bin/bash
#
# execute the actual plugin calculation via a docker container
#
DATE=date
if [ "$(uname)" == "Darwin" ]; then
  # date is gdate in Mac OS X.
  DATE=gdate
fi

echo ================================================================================
echo $($DATE --rfc-3339=seconds) $0 start
echo ================================================================================

DOCKER_IMAGE=$1
shift
INPUT_SERIES=$1
shift
JOB_DIR=$(dirname $1)
OUTPUT_DIR=$1
shift
LOG_DIR=$(dirname $1)
LOG_FILE=$(basename $1)

# TODO(billy): Either remove this or re-implement uid/gid/useradd magic in# Dockerfile after determining if it's necessary.
#
# # get the group id of the user executing the algorithm in the docker container
# GID=`docker run --rm ${DOCKER_IMAGE} "grep \\$(groups): /etc/group | cut -d: -f3"`
# echo ================================================================================ >> ${LOG_DIR}/run.log 2>&1
#
# echo $($DATE --rfc-3339=seconds) adjusting rights to group ${GID} > ${LOG_DIR}/run.log 2>&1
# # ensure write access to the job and log directory
# chgrp -R ${GID} ${JOB_DIR} ${LOG_DIR} >> ${LOG_DIR}/run.log 2>&1
# chmod -R g+w ${JOB_DIR} ${LOG_DIR} >> ${LOG_DIR}/run.log 2>&1
# ls -alR ${JOB_DIR} >> ${LOG_DIR}/run.log 2>&1
# echo ================================================================================ >> ${LOG_DIR}/run.log 2>&1

GPU_FLAG="--gpus all"
if ! [ -x "$(command -v nvidia-smi)" ]; then
  echo "nvidia-smi not detected. Running Docker image in CPU mode."
  GPU_FLAG=""
fi
docker run ${GPU_FLAG} --rm -v ${INPUT_SERIES}:/input -v ${OUTPUT_DIR}:/output -v ${LOG_DIR}:/logs ${DOCKER_IMAGE} --log_file=/logs/${LOG_FILE} > ${LOG_DIR}/run.log 2>&1

echo ================================================================================
echo $($DATE --rfc-3339=seconds) $0 finish
echo ================================================================================
