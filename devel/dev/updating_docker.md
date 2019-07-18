# How To Update - Upgrades for Docker Environment

## Frontend (React)

- Do the manual upgrades for the development environment (as per `updating_manually.md`).
- Don't forget to bump version in both code's `version.js` file and in `package.json`
- Run `deploy.sh` which copies over the updated package.json file to the Docker build environment.

## Backend (Python Django)

- Do the manual upgrades for the development environment (as per `updating_manually.md`).
- Run `deploy.sh` which copies over the updated package.json file to the Docker build environment.

## Local Testing

- Test the new build, by running the `docker-compose.yml` in the Docker development environment, which builds from the copied source code rather than pulls from GitHub (as would happen in production): `$ docker-compose up --force-recreate --remove-orphans --build`

## Deploy to Staging

- Change to the `frontend` directory in the Docker development environment
- Run `$ git add .`, `$ git commit -a` and `$ git push` to push changes to GitHub
- Change into the root directory of the Docker development environment
- Run `$ git add .`, `$ git commit -a` and `$ git push` to push changes to GitHub
- The pushes to GitHub should trigger automatic rebuilds of the Docker images on DockerHub, pulling the updated code from the GitHub repositories (both frontend - for the React client UI - and master - for the Django server)

## Staging Testing

- To test on the staging server, from the app's root directory, run: `$ docker-compose pull` to grab the updated images, then `$ docker-compose down` and `$ docker-compose up --force-recreate --remove-orphans --build` to rebuild the containers with the new code.

## Note: Changes to configuration files

Changes to _some_ files in the Docker environment's `config` directory - including `settings.py` - and the `docker-compose.yml` file in the Docker app root directory (but *not* python's requirements.txt) would need to be manually patched on those same files in the Docker development environment, and on the staging and production servers. This is because those files contain runtime configurations that are specific to their hosting environments, so cannot just be overwritten by new default versions. Changes to any of these files are *not* copied over from the code development environment to the Docker development environment when running `$ deploy.sh`.
