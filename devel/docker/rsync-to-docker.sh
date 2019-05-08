#!/bin/bash
## script to sync to staging server
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LOCAL_FRONTEND_BUILD_DIR="${DIR}/../../spm_frontend/react/build/"
LOCAL_DJANGO_API_CODE_PATH="${DIR}/../../spm_api/"
DOCKER_DJANGO_API_CODE_PATH="/home/dan/Data/LocalRepositories/DOCKER/SimplePhotoManagement/code/"
DOCKER_DJANGO_CONFIG_PATH="/home/dan/Data/LocalRepositories/DOCKER/SimplePhotoManagement/config/"
DOCKER_STATIC="/home/dan/Data/LocalRepositories/DOCKER/SimplePhotoManagement/static/"
# copy over api code
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${LOCAL_DJANGO_API_CODE_PATH} \
${DOCKER_DJANGO_API_CODE_PATH}
# copy over react frontend code
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${LOCAL_FRONTEND_BUILD_DIR} \
${DOCKER_STATIC}
# copy over config
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${DIR}/../../requirements.txt \
${DOCKER_DJANGO_CONFIG_PATH}