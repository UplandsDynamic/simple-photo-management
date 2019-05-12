# Simple Photo Management

**Important: Before scanning an image directory, please ensure you have backed up your data. This is a beta product and should be used with that in mind. Please do not put your only copy of digital photos at risk!**

This a simple application built on web technologies to IPTC tag, search & image optimise digital photo libraries.

It has web frontend client that connects to a RESTful API backend. Data is stored in either a SQLite, mySQL or PostgreSQL (recommended) database.

The web client is built with React.js and the server backend is written in Python 3.6 using the Django framework.

The `master` branch of this repository is source for the dockerised version of the server. Please checkout the `frontend` branch for source of the dockerised frontend web client.

The associated Docker images are available on DockerHub:

- Server:

  URL: <https://hub.docker.com/r/aninstance/simple-photo-management>

  To pull the image:

  `docker pull aninstance/simple-photo-management`

- Frontend client:

  URL: <https://hub.docker.com/r/aninstance/simple-photo-management-client>

  To pull the image:

  `docker pull aninstance/simple-photo-management-client`

- Docker Compose

  Please see an example docker-compose file (which builds the entire stack, including the web client & server) in the `master` (server) branch.

To use this source code for non-dockerised builds, please amend the settings.py configuration file accordingly.

## Key features

- Recursively scan directories for digital image files
- Add, remove & edit IPTC meta keyword tags from digital images via a web interface
- Automatically create a range of smaller (optimised) versions of each larger image (e.g. .jpg from a .tiff)
- Display & download optimised & resized versions of large images in the web interface
- Database IPTC tags associated with each image
- Search for & display digital images containing single IPTC tags or a combination of multiple tags

## Key technologies

- Python 3.7
- Django
- Django-rest-framework
- Javascript (ReactJS)
- HTML5
- CSS3

## How to use on Linux systems

To use the Docker images orchastrated with docker-compose:

- Create your app root directory & clone the repo into it:

  `mkdir spm`
  `cd spm`
  `git clone https://github.com/Aninstance/simple-photo-management.git .`

- Edit the following files to your specification:

  - `docker-compose-example.yml` - save as docker-compose.yml
  - `config/nginx/spm-example.config` - save as spm.conf
  - `config/.env.docker` - save as .env.docker (this is the frontend client configuration)

- Create the following directories in the application's root directory. These are for persistent storage (i.e. they persist even after the app server & client containers have been stopped, started, deleted, upgraded):

  - `mkdir photo_directory` - this is the directory where copies of your original images will be stored.
  - `mkdir media` - this is the directory where the processed images will be stored.
  - `mkdir static` - this is the directory where static content will be stored (including the client code).
  - `mkdir postgres` - this is the directory where the database will be located.
  - `mkdir -p log/gunicorn` - this is the directory where the logs will be located.

- You may remove the `src` directory, since the source will already be installed in the Docker image.

- Run this command to pull the Docker images and start the server (which serves both the server & frontend client components):

  `docker-compose up --build --force-recreate -d`

- If running for the first time (i.e. your persistent database folder is empty), define a superuser & by issuing the following commands:

  - Note down the name of the server app (exposing port 8000) that is output in the following command (e.g. `spm_app_1`):

    `docker-compose ps`

  - Run the following, substituting `spm_app_1` with the correct name for the server app, as discussed above.

    `docker exec -it smp_app_1 python manage.py createsuperuser`

- If running for the first time, create an `administrators` group and add the new user to it, as follows:

  - Login at the django admin url - e.g. http://your_domain.tld/admin/
  - Click `add` next to `Groups` in the `Authentication & Authorization` section.
  - Name the new group `administrators`.
  - Under `Available permissions`, scroll to the bottom and select all the `spm_app` permissions, clicking the arrow on the right to add these to the `Chosen permissions` pane (you may hold `shift` to select multiple at once). Once done, click `Save`.
  - Navigate to `Home > Users > your username` and scroll down to the `Permissions` section. Select `administrators` from the `Available groups` box and double-click it. This moves it to `Chosen groups`. Scroll to the bottom of the page and click `Save`.
  - Click `LOG OUT` (top right)

- Copy your original images (or directories of images) into the `photo_directory` directory.

- Navigate to the web client url - e.g. http://your_domain.tld

- Login to the web client using the superuser credentials you'd previously supplied.

- Click on the `+` button to scan the photo_directory for new original photos. By default, this action:
  - Recursively scans for digital images (.jpg, .tiff, .png)
  - Reads any IPTC keyword tags and adds them to the database.
  - The digital images are processed, with a range of image sizes automatically generated.
- Give it a few seconds and click the green refresh button (far left of the toolbar, beneath the page numbers). Images with no pre-existing IPTC keyword tags should be displayed (if any).
- To display images that do have tags, try typing a phrase into the search bar.
- Clicking the button with the `tag` icon re-scans all images in photo_directory, adds any newly discovered images and recopies all IPTC keyword tags to the database. To simply add new images without re-copying the tags, use the `+` button instead.
- Clicking the button with the `broom` icon cleans the database of references to any processed images that no longer exist in the `media` directories.
- Add new tags to an image by entering them in the input field, in the `Action` column. Separate multiple tags with a `/`. This action both writes the new tag(s) to the metadata of the **ORIGINAL IMAGE** and the database.
- The above guide is not definitive and is intended for users who know their way around Docker (and know how to troubleshoot!) If there are enough users of this app to warrant it, more thorough documentation would likely be made available. In the meantime, usage or installation questions can be sent to the contact details below.

## Screenshots

Coming soon ...

## Live Demo

There is a live demo available here:

Coming soon ...

## Development Roadmap

- Automated display of tag suggestions (based on real-time character matching & most used) when adding IPTC tags to an image
- Tag suggestions based on facial recognition

## Support

- Paid support services (including installation, configuration and development of bespoke features) are available. Please email productions@aninstance.com with "Simple Photo Management Support" in the subject field, or leave a message via the website form at: https://www.aninstance.com/contact

## Authors

- Dan Bright (Aninstance Consultancy), productions@aninstance.com
