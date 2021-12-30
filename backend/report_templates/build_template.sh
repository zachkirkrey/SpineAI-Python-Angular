#!/bin/sh

cd "$(dirname "$0")"

# Copy report.
cp -f ./src/*.html ./dist

# Copy assets.
mkdir -p ./dist/assets/img
cp -Rf ./src/assets/img/* ./dist/assets/img/
mkdir -p ./dist/assets/bin
cp -Rf ./src/assets/bin/* ./dist/assets/bin/

# TODO(billy): Remove for prod.
cp -Rf ./src/testdata/img/* ./dist/assets/img/

# Build SASS.
mkdir -p ./dist/assets/css
sass --update ./src/assets/scss:./dist/assets/css
