#!/bin/bash
set -e

echo "Running database migrations..."
python -m app.db.migrate

echo "Executing command..."
exec "$@"
