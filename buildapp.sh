#!/usr/bin/env bash
yarn --cwd frontend/ build
rm -rf ./assets
mv ./frontend/build ./assets
