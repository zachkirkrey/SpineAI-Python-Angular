#!/bin/sh
#
# Installation of Elastix plugin on ComputationNode
#

CN_ROOT=/var/cnroot
if [ "$(uname)" == "Darwin" ]; then
  # /var resolves to /private/var in Mac for Docker mounts.
  CN_ROOT=/private${CN_ROOT}
fi


# ================== BEGIN: Script parameters to be adjusted ================
# create a UID: python -c "import uuid; print str(uuid.uuid4()).upper()"
SCRIPT_UID=6C7EC70D-2D76-4181-8B38-3448D6BDD52D
SCRIPT_EXE=/bin/bash
SCRIPT_DIR=${CN_ROOT}/scripts/spineai
SCRIPT_MAIN=run.sh
SCRIPT_FILES=${SCRIPT_MAIN}
# =================== END: Script parameters to be adjusted =================

mkdir -p ${CN_ROOT}/plugins/${SCRIPT_UID}
mkdir -p ${SCRIPT_DIR}
echo $(date +'%Y-%m-%d %H:%M:%S') creating ${CN_ROOT}/plugins/${SCRIPT_UID}/config.json
perl -pe "s|\@Uid\@|${SCRIPT_UID}|; s|\@PluginPath\@|${SCRIPT_DIR}/${SCRIPT_MAIN}|; s|\@ExecutablePath\@|${SCRIPT_EXE}|;" config.json > ${CN_ROOT}/plugins/${SCRIPT_UID}/config.json

for f in ${SCRIPT_FILES}
do
    echo $(date +'%Y-%m-%d %H:%M:%S') copying $f
    cp $f ${SCRIPT_DIR}
done
