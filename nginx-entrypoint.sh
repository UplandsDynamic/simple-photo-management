#!/bin/sh
## startup script
cp -a /var/www/html/react/. /var/www/html/static/;
nginx -g 'daemon off;';

exec "$@"