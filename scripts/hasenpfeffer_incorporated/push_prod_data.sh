#!/bin/bash

# Fail the entire script when one of the commands in it fails
set -e

echo_usage() {
  echo "SYNOPSIS"
  echo "     ${0} -d db_connection [-a] [-i]"; echo
  echo "DESCRIPTION"
  echo "Available options"
  echo "     -d      Database connection information in the form 'host:port:database:username'. Required."
  echo "     -a      [OPTIONAL] Push all database tables including the canvas table."
  echo "     -i      [OPTIONAL] Mark all courses as inactive after push."
  echo "                 This may be desirable when populating a test environment."
}

# Default
inactivate_courses=false

while getopts "ad:i" arg; do
  case ${arg} in
    a)
      all_tables=true
      ;;
    d)
      # shellcheck disable=SC2206
      db_params=(${OPTARG//:/ })
      db_host=${db_params[0]}
      db_port=${db_params[1]}
      db_database=${db_params[2]}
      db_username=${db_params[3]}
      db_password=${db_params[4]}
      ;;
    i)
      inactivate_courses=true
      ;;
    *) ;;
  esac
done

# Validation
[[ "${db_host}" && "${db_port}" && "${db_database}" && "${db_username}" ]] || {
  echo; echo "[ERROR] You must specify complete database connection information."; echo
  echo_usage
  exit 1
}

if grep -qi prod <<< "${db_database}"; then
  echo; echo "[ERROR] The target database name (${db_database}) cannot contain 'prod'."; echo
  exit 1
fi

BR=$'\n\n'
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
CSV_HOME_DIRECTORY="${SCRIPT_DIR}/csv_files"
SQL_TRANSACTION="BEGIN;${BR}"

# Because of foreign key constraints, we must populate tables in order of association.
# TODO: When course-groups feature is live, add "course_groups course_group_memberships" after asset_categories below.
declare -a tables=(courses
                   users assets asset_users comments
                   activity_types activities
                   categories asset_categories
                   whiteboards whiteboard_users asset_whiteboard_elements whiteboard_elements)

# If requested, include the 'canvas' table.
if [[ "${all_tables}" ]]; then
  tables=(canvas ${tables[*]})
fi

# Verify the presence of CSV files.
for table in "${tables[@]}"; do
  csv_file="${CSV_HOME_DIRECTORY}/${table}.csv"
  [[ -f "${csv_file}" ]] || {
    echo "[ERROR] ${csv_file} not found. Aborting."
    exit 1
  }
done

if ! [[ "${db_password}" ]]; then
  echo -n "Enter database password: "
  read -s db_password; echo; echo
fi

echo "WARNING: You are on the verge of deleting ALL existing course and user data from the database '${db_database}' at ${db_host}:${db_port}."
echo -n "To accept the consequences, type 'consentio': "
read confirmation; echo

[[ "${confirmation}" = 'consentio' ]] || {
  echo "Aborting."
  exit 1
}

# Truncate!
if [[ "${all_tables}" ]]; then
  SQL_TRANSACTION+="TRUNCATE canvas CASCADE;${BR}"
fi

SQL_TRANSACTION+="TRUNCATE courses CASCADE;${BR}"
SQL_TRANSACTION+="TRUNCATE users CASCADE;${BR}"
SQL_TRANSACTION+="TRUNCATE categories CASCADE;${BR}"

push_csv() {
  # Format the header row as a comma-separated list for the Postgres copy command.
  header_row=$(head -1 "${CSV_HOME_DIRECTORY}/${1}.csv")
  columns=${header_row//|/,}

  # Load local CSV file contents into table.
  SQL_TRANSACTION+="\COPY ${1} (${columns}) FROM '${CSV_HOME_DIRECTORY}/${1}.csv' WITH (FORMAT CSV, HEADER TRUE, DELIMITER '|');${BR}"

  if [[ ${columns} == id* ]]; then
    # Tables with an auto-incrementing id column must reset the sequence after load.
    SQL_TRANSACTION+="SELECT setval('${1}_id_seq', (SELECT MAX(id) FROM ${1}));${BR}"
  fi
  if ${inactivate_courses} && [[ "${1}" == "courses" ]]; then
    # If requested, mark all courses as inactive.
    SQL_TRANSACTION+="UPDATE courses SET active = FALSE;${BR}"
  fi
}

# Push CSV file contents to the database.
for table in "${tables[@]}"; do
  push_csv "${table}"
done

SQL_TRANSACTION+="COMMIT;${BR}"

SQL_FILES="${SCRIPT_DIR}/local"
mkdir -p "${SQL_FILES}"

SQL_TRANSACTION_FILE="${SQL_FILES}/push_prod_data_$(date +%Y-%m-%d-%I%M%S).sql"
echo "${SQL_TRANSACTION}" | tee "${SQL_TRANSACTION_FILE}"

PGPASSWORD=${db_password} psql -h "${db_host}" -p "${db_port}" -d "${db_database}" --username "${db_username}" -f "${SQL_TRANSACTION_FILE}"

echo "Done."

exit 0
