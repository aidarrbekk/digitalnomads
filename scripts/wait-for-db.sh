#!/bin/bash
# Wait for PostgreSQL to be ready

set -e

host="$1"
port="${2:-5432}"
shift 2
cmd="$@"

until PGPASSWORD=medical_password psql -h "$host" -p "$port" -U "medical_user" -d "medical_qa" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
