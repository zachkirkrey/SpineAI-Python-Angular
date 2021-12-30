#!/bin/bash

cd "$(dirname "$0")/../.."
rm -f /tmp/database.db
mkdir -p /tmp/database_studies
cp -R ./testdata/dicom_ucla_BAAATUQQ /tmp/database_studies
poetry run python app.py --input_dir /tmp/database_studies --db_location /tmp/database.db --nodaemon
rm -rf /tmp/database_studies
cp -f /tmp/database.db ./testdata/database/database.db
