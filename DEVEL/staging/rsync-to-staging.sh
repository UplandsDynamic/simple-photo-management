#!/bin/bash
## script to sync to staging server
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
STAGING_SERVER="backup"
#LOCAL_BUILD_DIR="${DIR}/../../stock_control_frontend/react/build/"
#LOCAL_BUILD_STATIC_DIR="${DIR}/../../stock_control_frontend/react/build/static/"
STAGING_SERVER_DJANGO_PATH="/mnt/backupaninstancedatacenter/family-history-29032019-clone/spm/"
#STAGING_SERVER_REACT_PATH="/var/www/django/sm.staging.aninstance.com/react/"
STAGING_SERVER_STATIC_PATH="/mnt/backupaninstancedatacenter/family-history-29032019-clone/spm/static/"
STAGING_SERVER_MEDIA_PATH="/mnt/backupaninstancedatacenter/family-history-29032019-clone/spm/media/"
rsync -av --progress --exclude-from "${DIR}/rsync-ignore.txt" ${DIR}/../../ ${STAGING_SERVER}:${STAGING_SERVER_DJANGO_PATH}
#ssh ${STAGING_SERVER} rm -rf ${STAGING_SERVER_REACT_PATH};
#rsync -av --progress ${LOCAL_BUILD_DIR} ${STAGING_SERVER}:${STAGING_SERVER_REACT_PATH}
#rsync -av --progress ${LOCAL_BUILD_STATIC_DIR} ${STAGING_SERVER}:${STAGING_SERVER_STATIC_PATH}