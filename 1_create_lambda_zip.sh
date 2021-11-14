#!/bin/bash

OUTPUT_ZIP=deployment-package.zip
DEPLOY_DIR=./deploy
TMP_DIR=/tmp/loadshedding-stage-api-aws-deploy

rm -rf "$OUTPUT_ZIP" "$DEPLOY_DIR" "$TMP_DIR"
mkdir "$TMP_DIR"
cp -r ./ "$TMP_DIR"
mv "$TMP_DIR" "$DEPLOY_DIR"

pip install --target "$DEPLOY_DIR" -r ./requirements.txt
cd "$DEPLOY_DIR"
zip -r "../$OUTPUT_ZIP" .
cd ..

rm -rf "$DEPLOY_DIR" "$TMP_DIR"
