# Simple Photo Management

__Important: Before scanning an image directory, please ensure you have backed up your data. This is a beta product and should be used with that in mind. Please do not put your only copy of digital photos at risk!__

This a simple application built on web technologies to IPTC tag, search & image optimise digital photo libraries.

It has web frontend that connects to a RESTful API backend. Data is stored in either a SQLite, mySQL or PostgreSQL (recommended) database.

There is a web client (built with React.js) and a server backend (written in Python 3.6 using the Django framework).

This repository is for the dockerised version of the server. Please see aninstance/simple-photo-management-client for the frontend web client.

The associated Docker image is available on DockerHub:

<https://hub.docker.com/r/aninstance/simple-photo-management>

To pull the image: 

```docker pull aninstance/simple-photo-management```

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

## Screenshots

Coming soon ...

## Live Demo

There is a live demo available here:

Coming soon ...

## Development Roadmap

- Automated display of tag suggestions (based on realtime character matching & most used) when adding IPTC tags to an image
- Tag suggestions based on facial recognition

## Support

- Paid support services (including installation, configuration and development of bespoke features) are available. Please email productions@aninstance.com with "Simple Photo Management Support" in the subject field, or leave a message via the website form at: https://www.aninstance.com/contact

## Authors

- Dan Bright (Aninstance Consultancy), productions@aninstance.com
