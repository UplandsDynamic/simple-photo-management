# Simple Photo Management - Server Component

## About

This is a demo/prototype of simple application built on web technologies to IPTC tag, search & image optimise digital photo libraries.

It has web frontend client that connects to a RESTful API backend. Data is stored in either a SQLite, mySQL or PostgreSQL (recommended) database.

The web client is built with React.js and the server backend is written in Python 3.7 using the Django framework.

**Important: Before scanning an image directory, please ensure you have backed up your data. This is a prototype and should be used with that in mind. Please do not put your only copy of digital photos at risk!**

## Support & project status

A one-off installation service for this app is available. Please contact spm@uplandsdynamic.com for further details.

The GPL licensed version of this project offered here is *not guaranteed* to be regularly maintained. It is made available here for demo/prototype purposes only, and should not be used in production (i.e. a "live" working environment) unless the administrator regularly patches project dependencies (i.e. PYPI & npm packages) with upstream security updates as and when released by vendors.

## Key technologies

Python 3.7, Django, Django-rest-framework, Javascript (ReactJS), HTML5, CSS3

## Key features

- Recursively scan directories for digital image files
- Add, remove & edit IPTC meta keyword tags from digital images via a web interface
- Easily select previously used IPTC meta keyword tags and add to digital images
- Automatically create a range of smaller (optimised) versions of each larger image (e.g. .jpg from a .tiff)
- Optimised versions named using a hash of the origin image file, to prevent duplication (note, the hash includes metadata, so if an identical looking image has had a change in metadata it is deemed 'different'.)
- Display & download optimised & resized versions of large images in the web interface
- Database IPTC tags associated with each image
- Search for & display digital images containing single IPTC tags or a combination of multiple tags
- Search and replace IPTC tags over all scanned image directories
- Restrict access to specific tags for specific usernames
- Switch between `light` and `dark` modes (by setting an environment variable)

## Live Demo

There is a live demo available here:

https://frontend.spm.webapps.uplandsdynamic.com

Login credentials are:

- Username: riker
- Password: z4Xd\*7byV\$xw

## Screenshots

![Screenshot 1](./meta/img/screenshot_01.png?raw=true)

## Installation (on Linux systems)

__Below are basic steps to install and run a demonstration of the app on an Linux Ubuntu 20.04 server. They do not provide for a secure installation, such as would be required if the app was publicly available. Steps should be taken to security harden the environment if using in production.__

### Brief installation instructions

- Install EXIV2, EXIV2 development library and libboost development files, e.g.:

  - `apt install exiv2`
  - `apt install libexiv2-dev`
  - `apt install libboost-python-dev`

- Clone the repository to your file system.

- Ensure you have access to a current version of PostgreSQL (either locally installed, or remote).

- Ensure gunicorn is installed on your system.

- Create a system user under which to run the application (e.g. `django`). Recursively change ownership of the application directory and all its sub directories to that user, then switch to operate as that user.

- Change into the application's root directory.

- Install a python virtual environment on your system and make that your python source.

- Run `pip3 install -r requirements.txt`.

- Copy `spm_api/settings.DEFAULT.py` to `spm_api/settings.py`.

- Edit `spm_api/settings.py` according to your environment. Be sure to add the URL of your frontend web client to the CORS_ORIGIN_WHITELIST list property.

- Create the PostgreSQL database and user, as defined.

- Create a directory named `secret_key` in the application's root directory and change its ownership to the application user (as created above).

- Change permissions on the `secret_key` directory so only the user running the application can read it, e.g.: `chmod 0700 secret_key`.

- Create a systemd unit file to run the gunicorn service at `/etc/systemd/system/gunicorn.service`, then enable and start start the systemd service (details of how to do this is outwith the scope of this document, but if you need further advice feel free to get in touch).

- Create a systemd unit file to run the django_q service (which manages long running operations, such as 'stock taking') at `/etc/systemd/system/djangoq.service`. Enable and start the systemd service (details of how to do this is outwith the scope of this document, but if you need further advice feel free to get in touch).

- Install a web server (recommended Nginx) to operate as a reverse proxy and create an appropriate configuration file to connect to the unix socket created by gunicorn (as defined above). See the official Nginx and Django documentation for configuration examples.

- Create the following directories in the application's root directory (the paths to these need to be set in your settings.py):

  - `photo_directory` - this is the directory where copies of your original images will be stored.
  - `media/photos` - this is the directory where the processed images will be stored.
  - `media/photos_tn` - this is the directory where the processed thumbnail images will be stored.
  - `static` - this is the directory where static content will be stored.

- Copy your original images (or directories of images) into the `photo_directory` directory.

- As root (using sudo), create the log directory and file, e.g.:

  - `sudo mkdir -p /var/log/django;`
  - `sudo touch /var/log/django/spm.log`

- Change ownership of the log directory and its log file to the user running the app, e.g.:

  - `sudo chown -R django /var/log/django/`

- Create the database tables, using the commands:

  - `python manage.py makemigrations;`
  - `python manage.py makemigrations spm_app;`
  - `python manage.py migrate`.

- If running for the first time (i.e. your persistent database folder is empty), define a superuser by issuing the following commands from the application's root directory `python manage.py createsuperuser`.

- In the application's root directory, run `python manage.py collectstatic`, to add the static files to the appropriate directory (ensure the path to the `static` directory has been correctly configured in your web server configuration).

- Restart the gunicorn server, e.g.: `systemctl restart gunicorn.service`

- Now visit the app's administration area in your web browser (e.g. `https://your.domain.tld/admin`).

- If running for the first time, create an `administrators` group and add the new user to it, as follows:

  - Click `add` next to `Groups` in the `Authentication & Authorization` section.
  - Name the new group `administrators`.
  - Under `Available permissions`, scroll to the bottom and select all the `spm_app` permissions, clicking the arrow on the right to add these to the `Chosen permissions` pane (you may hold `shift` to select multiple at once). Once done, click `Save`.
  - Navigate to `Home > Users > your username` and scroll down to the `Permissions` section. Select `administrators` from the `Available groups` box and double-click it. This moves it to `Chosen groups`. Scroll to the bottom of the page and click `Save`.

- Click `LOG OUT` (top right)

- Login to the [web client](https://github.com/Aninstance/simple-photo-management-frontend) using the administrator user you created. Begin using Simple Photo Management.

### Update Instructions

- From the application's root directory, run `git pull`.
- Then, run `pip3 install -r requirements.txt`.
- Then, restart the gunicorn server: `systemctl restart gunicorn.service djangoq.service`.

## Brief UI instructions

Please see the repository for the frontend client, at https://github.com/Aninstance/simple-photo-management-frontend

Note: The above guide is not definitive and is intended for users who know their way around Ubuntu server and Django.

*Users would need to arrange database backups and to secure the application appropriately when used in a production environment.*

## Development Roadmap

- ~~Automated display of tag suggestions (based on real-time character matching & most used) when adding IPTC tags to an image~~ [Complete]
- Enhancement of `clean` to facilitate deletion of processed image files & thumbnails (rather just database entries) when origin image no longer exists
- Tag suggestions based on facial recognition
- Expose switching between `light` and `dark` modes on the UI rather than requiring setting of environment variable
- ~~Remove tags from the used-tag list if no longer used for any images~~ [Complete]
- ~~Add ability to delete tags after search (currently limited to replace with an alternative tag)~~ [Complete]

## Authors

- Dan Bright (Uplands Dynamic), dan@uplandsdynamic.com
