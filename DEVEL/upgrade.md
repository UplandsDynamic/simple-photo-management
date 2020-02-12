How To Update
=============

## Node (nmp)
NOTE: ONLY NEEDS DOING ON DEVELOPMENT SERVER, WHERE NODE BUILDS THE REACT WEBPACK PACKAGE

- First:
    - $ cd /LocalRespositories/DEVELOPMENT/StockManagement/stock_control_frontend/react
- In package.json, the follow 'semanic versioning' symbols are used, to restrict upgrades 
to patch, minor (point), or major:
    
    - Patch releases: "~" e.g. 1.0 or 1.0.x or ~1.0.4
    - Minor releases: "^" e.g. 1 or 1.x or ^1.0.4
    - Major releases: "*" e.g. Just * or x

- Then, to perform the upgrade:
    - $ npm update
    
- To view what upgrades are available for the VERY LATEST VERSIONS (ignoring semantic version
restrictions) - without actually performing the upgrade right away, run the npm-check-updates package (ncu):
    - ncu (if not installed, run: npm install -g npm-check-updates)
    
- Then, either upgrade certain packages to the VERY latest version, by selecting those you want to upgrade
and changing the semantic symbol and the version number to simply "*". Then run:

    - npm update
    
- Or, run ncu with the -u flag to update entire  - EVERYTHING, ALL PACKAGES in package.json to VERY LATEST, e.g.
   
    - ncu -u
    
## Python (pip)

NOTE: REMEMBER TO DO THIS ON THE PRODUCTION SERVER AS WELL AS IN DEVELOPMENT!

# setup
- Ensure the pip-tools package is installed in the venv:
    $ pip install pip-tools
- Ensure packages listed in requirements.in
- Generate the requirements.txt file, using pip-tools' 'pip-compile' command. This PINS to exact version numbers,
which is recommended for production & distribution (these can be upgraded periodically using the upgrade flag - 
see below in the #upgrading section:
    $ pip-compile requirements.in
- Sync the newly created requirements.txt file install everything in the venv:
    $ pip-sync
    
# upgrading
- $ cd /LocalRespositories/DEVELOPMENT/StockManagement
- Upgrade all packages to the latest version:
    $ pip-compile --upgrade
  Or, upgrade individual packages, to the latest version:
    $ pip-compile -P the_package_name (upgrades the_package_name to the very latest version)
  Or, upgrade individual packages to a specific version:
    $ pip-compile -P the_package_name==2.0.1 (upgrades the_package_name to version 2.0.1)
    
* Note, for more docs on pip-tools, see the github page at: https://github.com/jazzband/pip-tools