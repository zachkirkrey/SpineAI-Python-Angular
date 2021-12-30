#!/bin/bash
#
# build and test tasks of the ISD Example thresholding plugin
#

DOCKER_IMAGE=spineai/spineai_philips:prod
# adjust to comply to the user/group setup on your system
DOCKER_USERID=1000
DOCKER_GROUPID=100
CN_ROOT=/var/cnroot
SCRIPT_DIR=${CN_ROOT}/scripts/spineai
# create a UID: python.exe -c "import uuid; print(uuid.uuid4())"
JOB_ID=71022EE9-EA75-4724-810D-58C16884F50B
JOB_DIR=/var/cnroot/jobs/${JOB_ID}
JOB_LOG_DIR=/var/cnroot/JobLogs/${JOB_ID}

DATE=date
if [ "$(uname)" == "Darwin" ]; then
  # date is gdate in Mac OS X.
  DATE=gdate

  # /var resolves to /private/var in Mac for Docker mounts.
  CN_ROOT=/private${CN_ROOT}
  JOB_DIR=/private${JOB_DIR}
  JOB_LOG_DIR=/private${JOB_LOG_DIR}
fi

function init() {
    if [ ! -d ${CN_ROOT} ]
    then
        echo ===============================================================================
        echo $($DATE --rfc-3339=seconds) creating ${CN_ROOT} directories
        echo ===============================================================================
        sudo mkdir -m 775 -p ${CN_ROOT}/jobs ${CN_ROOT}/JobLogs ${CN_ROOT}/plugins ${CN_ROOT}/scripts
        sudo chgrp -R ${DOCKER_GROUPID} ${CN_ROOT}
    fi
}

function do_image {
    echo ===============================================================================
    echo $($DATE --rfc-3339=seconds) building docker image ${DOCKER_IMAGE}
    echo ===============================================================================
    docker pull ${DOCKER_IMAGE}
}

function do_clean {
    echo ===============================================================================
    echo $($DATE --rfc-3339=seconds) removing ${JOB_DIR}
    echo ===============================================================================
    rm -fr ${JOB_DIR}
}

function do_prepare {
    [ -z "$1" ] && set -- "testdata"
    rm -fr ${JOB_DIR}
    mkdir -p ${JOB_DIR}
    mkdir -p "${JOB_DIR}/inputparameters/input_series"
    cp ${1}/*.dcm "${JOB_DIR}/inputparameters/input_series/"
    mkdir -p ${JOB_DIR}/outputparameters
    rm -f ${JOB_DIR}/outputparameters/*.*
    rm -f ${JOB_LOG_DIR}/Log.txt
    mkdir -p ${JOB_LOG_DIR}
    sudo chgrp -R ${DOCKER_GROUPID} ${JOB_DIR} ${JOB_LOG_DIR}
    sudo chmod -R g+w ${JOB_DIR} ${JOB_LOG_DIR}
}

function do_shell {
    echo ===============================================================================
    echo $($DATE --rfc-3339=seconds) interactive shell in docker container of image ${DOCKER_IMAGE}
    echo ===============================================================================
    do_prepare
    cd ${JOB_DIR}
    docker run --rm -it -v ${JOB_DIR}:/data -v ${JOB_LOG_DIR}:/log --entrypoint /bin/bash ${DOCKER_IMAGE}
    cd -
}

function do_test {
    ./install.sh
    do_prepare ${1}
    /bin/bash ${SCRIPT_DIR}/run.sh ${DOCKER_IMAGE} "${JOB_DIR}/inputparameters/input_series" ${JOB_DIR}/outputparameters ${JOB_LOG_DIR}/Log.txt ${JOB_DIR}/Status.txt
    echo ===============================================================================
    cat ${JOB_LOG_DIR}/run.log
    echo ===============================================================================
    cat ${JOB_LOG_DIR}/Log.txt
    echo ===============================================================================
    ls -al ${JOB_DIR}/outputparameters
    echo ===============================================================================
}

init
case "$1" in
    "-h")
        echo "$0 [-h] [clean|image|shell|test]"
        ;;
    "clean")
        do_clean
        ;;
    "image")
        do_image
        ;;
    "shell")
        do_shell
        ;;
    "test")
        do_test
        ;;
    "test_axial")
        do_test testdata_axial
        ;;
    *)
        echo "ERROR: unknown task $1" 1>&2
        ;;
esac
