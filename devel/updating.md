# How To Update - Manual Upgrades for Development Environment

---

**NOTE: ALL BUILDING SHOULD BE DONE ON ADC (VIA SSH), AS A) QUICKER & B) `rsync-to-docker.sh` SCRIPT DEFINES THE PATHS ON ADC, NOT LOCAL MACHINES!**

---

## Node (npm)

- First, `$ cd /home/dan/dev/SimpleStockManagement/stock_control_frontend/react`
- To view what upgrades are available for the VERY LATEST VERSIONS (ignoring semantic version restrictions) - without actually performing the upgrade right away, run the npm-check-updates package (ncu) 
(Note: if ncu not installed, run:
  - Download and install NVM version manager from install scripts at `https://github.com/nvm-sh/nvm`, then `$ nvm use 15` (replace 15 with current latest major version)
    - *OR* if *NOT* running nvm version manager: `sudo su` & `curl -sL https://deb.nodesource.com/setup_15.x | bash -` (install *latest* NodeJS - not distro version - 12.x in this example). 
- Then, the following steps:
  - `sudo npm install -g npm-check-updates` (install ncu package)
  - `sudo npm install -g npx`) (install npx package, if not already installed)
  - 
- Run ncu with the -u flag to update *EVERYTHING*, *ALL PACKAGES* in package.json to *VERY LATEST*:
  -  Note: *ORDER OF THESE STEPS MATTERS!*
  - `$ ncu -u` (update the package.json to the latest package versions)
  - `$ rm -rf package-lock.json` (remove lock file)
  - `$ rm -rf node_modules` (delete existing node modules) 
  - `$ npm install` (install the packages)
  - 
- *NOW IF THERE ARE VULNARABILITIES FOUND, THE FOLLOWING STEPS*:
  - `$ npx npm-force-resolutions` (install a set of upgraded *package dependencies of installed packages* - necessary to patch security issues - first) 
  - `$ npm audit fix` (fix any outstanding issues)
- *OR*, if not upgrading everything (as above), upgrade only certain packages to the VERY latest version:
  -  Select packages you want to upgrade & change the semantic symbol and the version number to simply "*". 
  - `$ rm -rf node_modules` (delete existing packages)
  - `$ npm update` (update package.json to your specified versions)
  - `$npm install` (install the packages)
- *Note* if audit shows errors that cannot be fixed, try adding the latest version of the package (^) to the `resolutions` block of package.json.

Note: 'semantic versioning' symbols, used to restrict upgrades to patch, minor (point), or major, are as follows:
- Patch releases: "~" e.g. 1.0 or 1.0.x or ~1.0.4
- Minor releases: "^" e.g. 1 or 1.x or ^1.0.4
- Major releases: "*" e.g. Just * or x
  

## Python (pip)

### Set up

- First: `$ cd /home/dan/dev/SimpleStockManagement`
- Ensure venv exists & is built for the local system. If not, delete existing, and run:
  - `python3 -m venv .venv`
- Ensure the pip-tools package is installed in the venv: 
  - `$ pip install pip-tools`
- Generate the requirements.txt file, using pip-tools' 'pip-compile' command. This PINS to exact version numbers, which is recommended for production & distribution (these can be upgraded periodically using the upgrade flag - see below in the #upgrading section): 
  - `$ pip-compile --upgrade`
- Sync the newly created requirements.txt file install everything in the venv: 
  - `$ pip-sync`

### Upgrading

Ensure following commands are run on ADC (rather than local), otherwise paths will have to be modified


- Ensure in the virtual environment: 
  - `. venv/bin/activate.fish` (if using Fish shell)
- Upgrade all packages to the latest version: 
  - `$ pip-compile --upgrade`
  - Or, upgrade individual packages to the latest version: 
    - `$ pip-compile -P the_package_name` (upgrades the_package_name to the very latest version)
  - Or, upgrade individual packages to a specific version: 
    - `$ pip-compile -P the_package_name==2.0.1` (upgrades the_package_name to version 2.0.1)
- Then: `$ pip-sync` to actually do the upgrade now the versions have been set.

Note: for more docs on pip-tools, see the github page at: https://github.com/jazzband/pip-tools

## Deploy

*Ensure following commands are run on ADC (rather than local), otherwise paths will have to be modified*

- After updates complete, run the deploy.sh script to copy changes over to correct locations in the DOCKER directory
 - Then, commit changes to git & push to the adc git repository
 - Then, change to the DOCKER directory and:
   - Make any changes to README if necessary
   - Run `upgrade-docker-images.sh` to build the new images & push to the local Docker repo
   - Push DOCKER directory changes to Github
   - Pull new images for the app running in production & build the new containers & restart the apps.