#!/bin/bash

# Abort immediately if a command fails
set -e

echo; echo "Hello! Well what an excellent day for a PNG."

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}/.."
TARGET_JSON="${BASE_DIR}/tmp/elements.json"

cd "$BASE_DIR"

echo; echo '--- IMPORTANT ---'; echo
echo 'You must (1) set PNG_FOR_WHITEBOARD_ID env variable, and (2) confirm you are using proper version of Node.'

echo; echo 'First, we compile the 'whiteboard_to_png' Typescript file...'; echo

./scripts/compile_whiteboard_to_png.sh

echo; echo 'Next, pull sample whiteboard_elements JSON from Squiggy db.'; echo

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
echo -e "[$(cat "$TARGET_JSON")]" > "${TMP_JSON}"
sed '$!s/$/,/' "${TMP_JSON}" > "${TARGET_JSON}"
echo -e "[$(cat "${TARGET_JSON}")]" > "${TMP_JSON}"
mv "${TMP_JSON}" "${TARGET_JSON}"
# The TARGET_JSON file is now valid JSON.

echo; echo 'Finally, run the 'save_whiteboard_as_png.js' script.'; echo

PNG_FILE="${BASE_DIR}/tmp/whiteboard.png"

node \
  "${BASE_DIR}/scripts/node_js/save_whiteboard_as_png.js" \
  -b "${BASE_DIR}" \
  -w "${BASE_DIR}/tmp/elements.json" \
  -p "${PNG_FILE}"

echo; echo "Done! Your PNG file is ${PNG_FILE}"; echo

exit 0
