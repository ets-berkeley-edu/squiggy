#!/bin/bash

# Abort immediately if a command fails
set -e

echo -e "\nHello! Well what an excellent day for a PNG."

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR="${SCRIPT_DIR}/.."

mkdir -p "${BASE_DIR}/tmp"
TARGET_JSON="${BASE_DIR}/tmp/whiteboardElements.json"

cd "$BASE_DIR"

echo -e '\n--- IMPORTANT ---\n'
echo -e "You must\n  (1) set PNG_FOR_WHITEBOARD_ID env variable, and\n  (2) confirm you are using proper version of Node."

echo -e '\nFirst, we compile the 'whiteboard_to_png' Typescript file...\n'

./scripts/compile_whiteboard_to_png.sh

echo -e '\nNext, pull sample whiteboard_elements JSON from Squiggy db.\n'

# Construct an array of serialized whiteboard_elements, including z_index and uuid.
whiteboardElements='['

SQL="SELECT (json_build_object('element', element, 'uuid', uuid, 'zIndex', z_index) || ',') AS whiteboard_element FROM whiteboard_elements WHERE whiteboard_id = ${PNG_FOR_WHITEBOARD_ID}"

while read row
do
  whiteboardElements+="${row}"
done <<< $(psql \
  --field-separator ' ' \
  --no-align \
  --quiet \
  --set AUTOCOMMIT=off \
  --set ON_ERROR_STOP=on \
  --single-transaction \
  -c "${SQL}" \
  -h localhost \
  -p 65432 \
  -t \
  -U app_squiggy \
  -X \
  squiggy_dev)

# Remove trailing comma and append right-bracket to close the array.
whiteboardElements=$(echo "${whiteboardElements}" | awk 'gsub(/,$/,x)')
whiteboardElements+="]"
echo -e "${whiteboardElements}" > "${TARGET_JSON}"

echo -e "\nGenerated JSON file: ${TARGET_JSON}\n"

echo -e '\nFinally, run the 'save_whiteboard_as_png.js' script.\n'

PNG_FILE="${BASE_DIR}/tmp/whiteboard.png"

node \
  "${BASE_DIR}/scripts/node_js/save_whiteboard_as_png.js" \
  -b "${BASE_DIR}" \
  -p "${PNG_FILE}" \
  -w "${TARGET_JSON}" \
  -v true

echo -e "\nPNG file: ${PNG_FILE}\n\nBye!\n"

exit 0
