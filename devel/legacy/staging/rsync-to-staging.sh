#!/bin/bash
## script to sync to staging server
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
STAGING_SERVER="backup"
LOCAL_BUILD_DIR="${DIR}/../../spm_frontend/react/build/"
LOCAL_BUILD_STATIC_DIR="${DIR}/../../spm_frontend/react/build/static/"
STAGING_SERVER_DJANGO_PATH="/mnt/backupaninstancedatacenter/spm/"
STAGING_SERVER_REACT_PATH="/var/www/spm/react/"
STAGING_SERVER_STATIC_PATH="/var/www/spm/static/"
STAGING_SERVER_MEDIA_PATH="/var/www/spm/media/"
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${DIR}/../../ ${STAGING_SERVER}:${STAGING_SERVER_DJANGO_PATH}
ssh ${STAGING_SERVER} rm -rf ${STAGING_SERVER_REACT_PATH};
rsync -av --progress ${LOCAL_BUILD_DIR} ${STAGING_SERVER}:${STAGING_SERVER_REACT_PATH}
rsync -av --progress ${LOCAL_BUILD_STATIC_DIR} ${STAGING_SERVER}:${STAGING_SERVER_STATIC_PATH}