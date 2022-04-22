#!/bin/bash

# Abort immediately if a command fails
set -e

# Install dependencies
npm list | grep typescript || npm install -g typescript
npm list | grep fabric || npm install -g fabric

echo; echo 'Compiling...'; echo

cd "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)/.."

# When deploying to AWS Elastic Beanstalk, this compilation happens in buildspec.yml.
tsc --resolveJsonModule --esModuleInterop scripts/node_js/save_whiteboard_as_png.ts

echo; echo 'Done.'; echo

exit 0
