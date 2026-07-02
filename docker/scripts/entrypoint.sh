#!/bin/sh
set -e

mkdir -p /app/storage/uploads
chown -R 1000:1000 /app/storage/uploads

exec gosu 1000:1000 "$@"