#!/bin/bash
## script to sync to staging server
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LOCAL_FRONTEND_DIR="${DIR}/../../spm_frontend/react/"
LOCAL_DJANGO_API_CODE_PATH="${DIR}/../../spm_api/"
DOCKER_DJANGO_API_CODE_PATH="/home/dan/Data/LocalRepositories/DOCKER/SimplePhotoManagement/src/"
DOCKER_DJANGO_CONFIG_PATH="/home/dan/Data/LocalRepositories/DOCKER/SimplePhotoManagement/config/"
DOCKER_FRONTEND="/home/dan/Data/LocalRepositories/DOCKER/SimplePhotoManagement/frontend/public/"
# copy over api code
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${LOCAL_DJANGO_API_CODE_PATH} \
${DOCKER_DJANGO_API_CODE_PATH}
# copy over react frontend src code (inc. .js)
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${LOCAL_FRONTEND_DIR} \
${DOCKER_FRONTEND}
# copy over requirements.txt
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${DIR}/../../requirements.txt \
${DOCKER_DJANGO_CONFIG_PATH}