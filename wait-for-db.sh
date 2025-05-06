#!/bin/sh

set -e

host="$1"
shift
cmd="$@"

until mysqladmin ping -h "$host" --silent; do
  echo "Waiting for MySQL..."
  sleep 1
done

>&2 echo "MySQL is up - executing command"
exec $cmd
