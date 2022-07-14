#!/bin/bash

# Abort immediately if a command fails
set -e

echo -e "\nHello! Well what an excellent day for a PNG."

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}/.."

mkdir -p "${BASE_DIR}/tmp"
TARGET_JSON="${BASE_DIR}/tmp/elements.json"

cd "$BASE_DIR"

echo -e '\n--- IMPORTANT ---\n'
echo -e "You must\n  (1) set PNG_FOR_WHITEBOARD_ID env variable, and\n  (2) confirm you are using proper version of Node."

echo -e '\nFirst, we compile the 'whiteboard_to_png' Typescript file...\n'

./scripts/compile_whiteboard_to_png.sh

echo -e '\nNext, pull sample whiteboard_elements JSON from Squiggy db.\n'

SQL="SELECT element FROM whiteboard_elements WHERE whiteboard_id = ${PNG_FOR_WHITEBOARD_ID}"

psql -c "${SQL}" \
  -h localhost \
  --output="${TARGET_JSON}" \
  -p 65432 \
  -t \
  -U app_squiggy \
  squiggy_dev

# Convert db result-set to valid JSON.
TMP_JSON="${BASE_DIR}/tmp/tmp.json"
echo -e "[$(cat "${TARGET_JSON}")]" > "${TMP_JSON}"
sed '$!s/$/,/' "${TMP_JSON}" > "${TARGET_JSON}"
rm "${TMP_JSON}"
# The TARGET_JSON file is now valid JSON.

echo -e "\nGenerated JSON file: ${TARGET_JSON}\n"

echo -e '\nFinally, run the 'save_whiteboard_as_png.js' script.\n'

PNG_FILE="${BASE_DIR}/tmp/whiteboard.png"

node \
  "${BASE_DIR}/scripts/node_js/save_whiteboard_as_png.js" \
  -b "${BASE_DIR}" \
  -p "${PNG_FILE}" \
  -w "${BASE_DIR}/tmp/elements.json" \
  -v true

echo -e "\nPNG file: ${PNG_FILE}\nDone.\n"

exit 0
