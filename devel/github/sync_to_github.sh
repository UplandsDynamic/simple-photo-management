#!/bin/bash
## script to sync development directory to github directory, then push any changes to github.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
WORKING_DIR=${DIR}
GITHUB_DIR="/home/dan/LocalRepositories/GITHUB/SimplePhotoManagement"
BRANCH="devel"  # master | devel

function choose_branch () {
if [[ -z $1 ]]
then
read -p "Branch to push to [master(m)|devel(d)]: " branch
else
branch=$1
fi
if [[ "${branch}" == "master" || "${branch}" ==  "m" ]]
then
BRANCH="master";
elif [[ "${branch}" == "devel" || "${branch}" ==  "d" ]]
then
BRANCH="devel";
else
printf "\nInput not recognised!\n\n"
exit 1
fi
printf "\n\nWORKING ON THIS BRANCH: %s \n\n" "${BRANCH}"
}

function push_to_github () {
cd "${GITHUB_DIR}" || exit;
git checkout "${BRANCH}";
cd "${WORKING_DIR}" || exit;
rsync -av --exclude-from ${WORKING_DIR}/rsync_github_exclude.txt ${WORKING_DIR}/../../ ${GITHUB_DIR}/
cd "${GITHUB_DIR}" || exit;
git add .
if [[ -z $1 ]]
then
git commit -a
else
git commit -am "$1"
fi
git push origin "${BRANCH}";
printf "\nPushed to Github!\n";
}

choose_branch "$1"
push_to_github "$2";