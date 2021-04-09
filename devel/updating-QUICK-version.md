# Quick updating

Assumes toolchain is installed etc

## On local or remote system

### backend server

`pip-compile --upgrade`

### frontend api

- `bash`
- `cd spm_frontend/react`
- `ncu -u`
- update version number in `package.json` & `src/version.js`

## On remote system

- `./devel/deploy.sh`
- `git add .` `git commit -a` `git push`
- `cd ../../DOCKER/SimplePhotoManagement/`
- `./upgrade-docker-images.sh`
- `git add .` `git commit -a` `git push`
- `cd frontend`
- `git add .` `git commit -a` `git push`