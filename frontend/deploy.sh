#!/bin/bash

(
  echo "Building front-end"
  rm -rf static/
  rm static.zip
  npm run build
  mv build static
  zip -r static.zip static/
  echo "Done building front-end"
) &

wait