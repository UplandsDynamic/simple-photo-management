# Simple Photo Management

**Important: Before scanning an image directory, please ensure you have backed up your data. This is a beta product and should be used with that in mind. Please do not put your only copy of digital photos at risk!**

This a simple application built on web technologies to IPTC tag, search & image optimise digital photo libraries.

It has web frontend client that connects to a RESTful API backend. Data is stored in either a SQLite, mySQL or PostgreSQL (recommended) database.

The web client is built with React.js and the server backend is written in Python 3.6 using the Django framework.

## Screenshots

![Screenshot 1](./meta/img/screenshot_01.png?raw=true)

## Live Demo

There is a live demo available here:

http://spm.staging.aninstance.com

Login credentials are:

- Username: riker
- Password: z4Xd\*7byV\$xw

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
- Switch between `light` and `dark` modes (by setting an environment variable)

## Key technologies

- Python 3.7
- Django
- Django-rest-framework
- Javascript (ReactJS)
- HTML5
- CSS3

## Docker deployment

The `master` branch of this repository is source for the dockerised version of the server. Please checkout the `frontend` branch for source of the dockerised frontend web client.

If deploying with Docker, it is highly recommended to use Docker Compose. Please find an example docker-compose file (which builds the entire stack, including the web client & server) in the `master` (server) branch.

The associated Docker images for server and client are available on DockerHub:

- Server:

  URL: <https://hub.docker.com/r/aninstance/simple-photo-management>

  To pull the image:

  `docker pull aninstance/simple-photo-management`

- Frontend client:

  URL: <https://hub.docker.com/r/aninstance/simple-photo-management-client>

  To pull the image:

  `docker pull aninstance/simple-photo-management-client`

To use this source code for non-dockerised builds, please amend the settings.py configuration file accordingly.

## Installation (on Linux systems)

**Note: These are basic instructions to install and run the app for demonstration purposes only and do not provide for a secure installation, such as would be required if the app was publicly available. Steps should be taken to harden the environment if using in production, such as applying suitable file & directory permissions; serving over a TLS connection; and running the Docker containers as a user other than root.**

To use the Docker images orchestrated with docker-compose:

- Create your app root directory & clone the repository into it:

  `mkdir spm`
  `cd spm`
  `git clone https://github.com/Aninstance/simple-photo-management.git .`

- Edit the following files to your specification:

  - `docker-compose-example.yml` - save as docker-compose.yml
  - `config/nginx/spm-example.config` - save as spm.conf
  - `config/.env.docker` - save as .env.docker (this is the frontend client configuration, where you may configure things like the number of items displayed per page)

  **Note: Don't forget to set the URL in both the `docker-compose.yml` (`app`'s `APP_URL` variable) and the `.env.docker` (`REACT_APP_ROUTE`, `REACT_APP_API_ROUTE` & `REACT_APP_API_DATA_ROUTE` variables) files (as above).**

- Create the following directories in the application's root directory. These are for persistent storage (i.e. they persist even after the app server & client containers have been stopped, started, deleted, upgraded):

  - `mkdir photo_directory` - this is the directory where copies of your original images will be stored.
  - `mkdir -p media/photos` - this is the directory where the processed images will be stored.
  - `mkdir -p media/photos_tn` - this is the directory where the processed thumbnail images will be stored.
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

## Usage Instructions

- Navigate to the web client url - e.g. http://your_domain.tld **Note: When starting a newly built or pulled container for the first time, the web client may take several minutes (depending on your server's resources) to create a fresh build. You will get a `502 Bad Gateway` error whilst the NPM build is occurring. Please be patient and try refreshing the page in a few moments.**

- Login to the web client using the superuser credentials you'd previously supplied.

- Click on the `+` button to scan the photo_directory for new original photos. By default, this action:
  - Recursively scans for digital images (.jpg, .tiff, .png)
  - Reads any IPTC keyword tags and adds them to the database.
  - The digital images are processed, with a range of image sizes automatically generated.
- Give it a few seconds and click the green refresh button (far left of the toolbar, beneath the page numbers). Images with no pre-existing IPTC keyword tags should be displayed (if any).
- To display images that do have tags, try typing a phrase into the search bar:
  - To search for tags containing a specifically defined phrase, enclose the phrase between quotation marks, e.g. "a phrase tag"
  - To search for images that contain a combination of multiple tags, separate search words or phrases with either a space, or a forward slash `/`.
- Clicking the button with the `tag` icon re-scans all images in photo_directory, adds any newly discovered images and recopies all IPTC keyword tags to the database. To simply add new images without re-copying the tags, use the `+` button instead.
- Clicking the button with the `broom` icon cleans the database of references to any processed images that no longer exist in the `media` directories or the origin image `photo_directory`.
- Clicking the button with the `swap` icon (left & right arrows) switches to `search & replace` mode, which allows replacement of an IPTC tag in all images with another:
  -Simply enter the term to search for in the upper `Search` field, the replacement tag in the `Replace` field, then click on the red button to `search & replace`.
- Add new tags to an image in one of two ways. These actions both write the new tag(s) to the metadata of the **ORIGINAL IMAGE** and to the database.:
  - By entering them in the input field, in the `Action` column. Separate multiple tags with a `/`.
  - By selecting from the list of previously used tags, that appears below the input field after you've begun to enter your tag. As you continue to type, this list resolves to display tags containing a sequence of characters that match your input.

## Documentation

The above guide is not definitive and is intended for users who know their way around Docker (and know how to troubleshoot!) If there are enough users of this app to warrant it, more thorough documentation would likely be made available. In the meantime, usage or installation questions can be sent to the contact details below.

## Development Roadmap

- ~~Automated display of tag suggestions (based on real-time character matching & most used) when adding IPTC tags to an image~~ [Complete]
- Enhancement of `clean` to facilitate deletion of processed image files & thumbnails (rather just database entries) when origin image no longer exists
- Tag suggestions based on facial recognition
- Expose switching between `light` and `dark` modes on the UI rather than requiring setting of environment variable
- Remove tags from the used-tag list if no longer used for any images

## Support

- Paid support services (including installation, configuration and development of bespoke features) are available. Please email productions@aninstance.com with "Simple Photo Management Support" in the subject field.

## Authors

- Dan Bright (Aninstance Consultancy), productions@aninstance.com
