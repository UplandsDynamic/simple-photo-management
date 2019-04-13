#!/usr/bin/env bash

#######
## Author: Dan Bright, productions@aninstance.com
##
## This script does the following:
##
## If git branch is 'devel':
##   - commits and pushes to git repository, devel branch
##   - deploys devel branch to staging server
##
## If git branch is 'master':
##   - merges devel branch into master
##   - commits and pushes to git repository, master branch
##   - commits and pushes to github repository, master branch
##   - deploys master branch to production server
##
## Notes:
##  General:
##      - Servers and other configurations are defined in the script variables.
##  Referenced in code:
##      1. Sets same version in production, so it tracks dev version when merged & deployed.
##      2. "If" statement only pushes to github if on branch master (production). To push to a
##         devel branch on github, remove the "if" statement.
#######

set e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
PROJECT_ROOT_DIR="${SCRIPT_DIR}/.."
API_APP_DIR="${PROJECT_ROOT_DIR}/spm_api"
FRONTEND_DIR="${PROJECT_ROOT_DIR}/spm_frontend/react"
BUILD_DIR="${FRONTEND_DIR}/build"
GIT_BRANCH=''
GITHUB_SCRIPT="${SCRIPT_DIR}/github/sync_to_github.sh"
COMMIT_MESSAGE="Default automated deploy comment"
PROJECT_TESTS_FILE="spm_app.tests"

function deploy {
run_django_tests
if [[ "$(git branch)" == *"* master"* ]]
then
GIT_BRANCH='master'
sync_to_production;
elif [[ "$(git branch)" == *"* devel"* ]]
then
GIT_BRANCH='devel'
sync_to_staging;
else
printf "\nNot working on a defined sync branch, so not syncing!\n\n"
fi
}

function run_django_tests {
cd ${PROJECT_ROOT_DIR}
echo "DEVEL" > ./run_type.txt
cd ${API_APP_DIR}
${PROJECT_ROOT_DIR}/venv/bin/python3 manage.py test ${PROJECT_TESTS_FILE}
proceed
}

function proceed() {
printf '\n'
read -p "Proceed ${1} (y/n) [n aborts deployment]: " confirm
if [[ "${confirm}" == "Y" || "${confirm}" ==  "y" ]]
then
return
elif [[ "${confirm}" == "N" || "${confirm}" ==  "n" ]]
then
exit 11
else
printf "\nInput not recognised!\n\n"
proceed;
fi
}

function get_version {
read -p "Version number (e.g. 2.3.6): " version
echo ${version}
}

function git_repos_commit_and_push {
cd ${PROJECT_ROOT_DIR}
if [[ "$(git status)" != *"nothing to commit"* ]]
then
echo "Enter git commit message (ctl-d twice to finish)"
message=$(cat)
git add .
git commit -am "${message}"
proceed
fi
if [[ ${GIT_BRANCH} == 'master' ]]
then
git merge devel
proceed
fi
git push
printf "\nPushed to git repository!\n\n"
if [[ ${GIT_BRANCH} == 'master' ]]  ## see note 2 (up top)
then
proceed 'to next step: push to GitHub?'
github_commit_and_push "$message"
fi
}

function github_commit_and_push () {
${GITHUB_SCRIPT} ${GIT_BRANCH} "$1"
proceed
}

function sync_to_production {
REMOTE_DIR=""
REMOTE_API_DIR=""
REMOTE_SERVICE_NAME=""
REACT_ENV_FILE="${FRONTEND_DIR}/.env.production"
REMOTE_SERVER_SSH_HOST=""
printf "\nWorking on branch: master, deploying to PRODUCTION!\n\n"
cd ${FRONTEND_DIR}
# sed -i "/REACT_APP_VERSION/c\REACT_APP_VERSION = '$(get_version)'" ${REACT_ENV_FILE}  # no need if want to track dev version number
cd ${PROJECT_ROOT_DIR}
git_repos_commit_and_push
echo "PRODUCTION" > ./run_type.txt
cd ${API_APP_DIR}
../venv/bin/python3 manage.py check --deploy
proceed
rm -rf ${BUILD_DIR}
cd ${FRONTEND_DIR}
npm run build:production
${SCRIPT_DIR}/prod/rsync-to-prod.sh
ssh ${REMOTE_SERVER_SSH_HOST} "${REMOTE_DIR}/venv/bin/python3 ${REMOTE_API_DIR}/manage.py collectstatic --noinput"
ssh ${REMOTE_SERVER_SSH_HOST} "chown -R django ${REMOTE_DIR}"
ssh ${REMOTE_SERVER_SSH_HOST} systemctl restart ${REMOTE_SERVICE_NAME}
#ssh ${REMOTE_SERVER_SSH_HOST}  "pkill -f \"python manage.py qcluster\"" # kill django_q worker processes
ssh ${REMOTE_SERVER_SSH_HOST} "${REMOTE_DIR}/venv/bin/python3 ${REMOTE_API_DIR}/manage.py qcluster"  # restart django_q
echo "DEVEL" > ${PROJECT_ROOT_DIR}/run_type.txt
printf "\nDEPLOYED TO PRODUCTION!\n\n"
}

function sync_to_staging {
REMOTE_DIR="/mnt/backupaninstancedatacenter/family-history-29032019-clone/spm"
REMOTE_API_DIR="/mnt/backupaninstancedatacenter/family-history-29032019-clone/spm/spm_api"
REMOTE_SERVICE_NAME="spm.staging.gunicorn.service"
REACT_ENV_FILE="${FRONTEND_DIR}/.env.staging"
REACT_ENV_FILE_PROD="${FRONTEND_DIR}/.env.production"
REMOTE_SERVER_SSH_HOST="backup"
VERSION=$(get_version)
printf "\nWorking on branch: devel, deploying to STAGING!\n\n"
cd ${FRONTEND_DIR}
sed -i "/REACT_APP_VERSION/c\REACT_APP_VERSION = '${VERSION}'" ${REACT_ENV_FILE}
sed -i "/REACT_APP_VERSION/c\REACT_APP_VERSION = '${VERSION}'" ${REACT_ENV_FILE_PROD}  # see Note (1) (up top)
cd ${PROJECT_ROOT_DIR}
git_repos_commit_and_push
echo "STAGING" > ./run_type.txt
cd ${API_APP_DIR}
../venv/bin/python3 manage.py check --deploy
proceed
rm -rf ${BUILD_DIR}
cd ${FRONTEND_DIR}
npm run build:staging
${SCRIPT_DIR}/staging/rsync-to-staging.sh
ssh ${REMOTE_SERVER_SSH_HOST} "${REMOTE_DIR}/venv/bin/python3 ${REMOTE_API_DIR}/manage.py collectstatic --noinput"
ssh ${REMOTE_SERVER_SSH_HOST} "chown -R dan ${REMOTE_DIR}"
ssh -t ${REMOTE_SERVER_SSH_HOST} "sudo systemctl restart ${REMOTE_SERVICE_NAME}"
ssh ${REMOTE_SERVER_SSH_HOST} "pkill -f \"python manage.py qcluster\""  # kill django_q worker processes
#ssh ${REMOTE_SERVER_SSH_HOST} "${REMOTE_DIR}/venv/bin/python3 ${REMOTE_API_DIR}/manage.py qcluster"  # restart django_q
echo "DEVEL" > ${PROJECT_ROOT_DIR}/run_type.txt
printf "\nDEPLOYED TO STAGING!\n\n"
}

deploy