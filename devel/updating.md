# How To Update - Manual Upgrades for Development Environment

## Node (npm)

- First, `$ cd /home/dan/dev/SimplePhotoManagement/smp_frontend/react`
- To view what upgrades are available for the VERY LATEST VERSIONS (ignoring semantic version restrictions) - without actually performing the upgrade right away, run the npm-check-updates package (ncu) (Note: if ncu not installed, run: npm install -g npm-check-updates *and* npm install -g npx)
- Run ncu with the -u flag to update *EVERYTHING*, *ALL PACKAGES* in package.json to *VERY LATEST*: `$ ncu -u`, delete existing `$ rm -rf node_modules`, then `$ npx npm-force-resolutions`, then `$ npm install`
- *OR*, if not upgrading everything (as above), upgrade only certain packages to the VERY latest version, by selecting those you want to upgrade
    and changing the semantic symbol and the version number to simply "*". Then delete existing `$ rm -rf node_modules`. Then run: `$ npm update`
- *Note* if audit shows errors that cannot be fixed, try adding the latest version of the package (^) to the `resolutions` block of package.json.

Note: 'semantic versioning' symbols, used to restrict upgrades to patch, minor (point), or major, are as follows:

    - Patch releases: "~" e.g. 1.0 or 1.0.x or ~1.0.4
    - Minor releases: "^" e.g. 1 or 1.x or ^1.0.4
    - Major releases: "*" e.g. Just * or x

## Python (pip)

### Set up

- Ensure the pip-tools package is installed in the venv: `$ pip install pip-tools`
- Ensure packages listed in requirements.in
- Generate the requirements.txt file, using pip-tools' 'pip-compile' command. This PINS to exact version numbers, which is recommended for production & distribution (these can be upgraded periodically using the upgrade flag - see below in the #upgrading section): `$ pip-compile requirements.in`
- Sync the newly created requirements.txt file install everything in the venv: `$ pip-sync`

### Upgrading

- First: `$ cd /home/dan/dev/SimplePhotoManagement`
- Ensure in the virtual environment: `. venv/bin/activate.fish` (if using Fish shell)
- Upgrade all packages to the latest version: `$ pip-compile --upgrade`, or upgrade individual packages, to the latest version: `$ pip-compile -P the_package_name` (upgrades the_package_name to the very latest version), or upgrade individual packages to a specific version: `$ pip-compile -P the_package_name==2.0.1` (upgrades the_package_name to version 2.0.1)
- Then: `$ pip-sync` to actually do the upgrade now the versions have been set.

Note: for more docs on pip-tools, see the github page at: https://github.com/jazzband/pip-tools

## Issues

- If running into a problem upgrading py3exiv2, try symlinking the liboost_python-py3(x).so files, e.g.: `ln -s /usr/lib/x86_64-linux-gnu/libboost_python-py36.so /usr/lib/libboost_python36.so`