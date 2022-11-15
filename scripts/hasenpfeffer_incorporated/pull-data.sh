#!/bin/bash

# Fail the entire script when one of the commands in it fails
set -e

echo_usage() {
  echo "SYNOPSIS"
  echo "     ${0} -d db_connection [-c canvas_hostname [-r replacement_canvas_hostname]] [-a]"; echo
  echo "DESCRIPTION"
  echo "Available options"
  echo "     -d      Database connection information in the form 'host:port:database:username'"
  echo "     -a      [OPTIONAL] Pull all database tables including the canvas table."
  echo "     -c      [OPTIONAL] Hostname of the Canvas instance for which SuiteC course data should be pulled."
  echo "                 Defaults to all instances."
  echo "     -r      [OPTIONAL] If provided, all references to Canvas-hosted resources will be changed to this hostname."
  echo "                 You must include the '-c' flag when using this option."
}

while getopts "ac:d:r:" arg; do
  case ${arg} in
    a)
      all_tables=true
      ;;
    c)
      source_canvas="${OPTARG}"
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
    r)
      replacement_canvas="${OPTARG}"
      ;;
    *) ;;
  esac
done

# Validation
[[ "${db_host}" && "${db_port}" && "${db_database}" && "${db_username}" ]] || {
  echo "[ERROR] You must specify complete database connection information."; echo
  echo_usage
  exit 1
}
[[ "${replacement_canvas}" ]] && ! [[ "${source_canvas}" ]] && {
  echo "[ERROR] A replacement Canvas hostname cannot be specified without also specifying a source Canvas instance."; echo
  echo_usage
  exit 1
}

if ! [[ "${db_password}" ]]; then
  echo -n "Enter database password: "
  read -s db_password; echo; echo
fi

if [[ "${replacement_canvas}" ]]; then
  echo "Will pull data for all courses hosted under ${source_canvas}, changing host references to ${replacement_canvas}."
elif [[ "${source_canvas}" ]]; then
  echo "Will pull data for all courses hosted under ${source_canvas}."
else
  echo "Will pull data for all courses."
fi
echo

SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
CSV_HOME_DIRECTORY="${SCRIPT_DIR}/csv_files"

mkdir -p "${CSV_HOME_DIRECTORY}"

output_csv() {
  # Connect to the source database and pipe the results of a supplied query to a CSV file in the local directory.
  echo "Copying ${1} from database..."
  PGPASSWORD=${db_password} psql -h "${db_host}" -p "${db_port}" -d "${db_database}" --username "${db_username}" \
  -c "COPY (${2}) TO STDOUT WITH (FORMAT CSV, HEADER TRUE, FORCE_QUOTE *, DELIMITER '|')" > "${CSV_HOME_DIRECTORY}/${1}.csv"
}

# Query each table for data associated with the supplied Canvas instance. The only table we do not query is the
# 'canvas' table itself.

# First, pull data from tables that contain no references to specific Canvas hostnames. Select by Canvas instance
# if that option is specified.

if [[ "${source_canvas}" ]]; then

  output_csv "activities" "SELECT a.* FROM activities a
              JOIN courses c
              ON a.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'
              order by id"

  output_csv "activity_types" "SELECT at.* FROM activity_types at
              JOIN courses c
              ON at.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "asset_categories" "SELECT ac.* FROM asset_categories ac
              JOIN (categories cat JOIN courses c
                ON cat.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON ac.category_id = cat.id"

  output_csv "asset_users" "SELECT au.* FROM asset_users au
              JOIN (users u JOIN courses c
                ON u.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON au.user_id = u.id"

  output_csv "categories" "SELECT cat.* FROM categories cat
              JOIN courses c
              ON cat.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "comments" "SELECT com.* FROM comments com
              JOIN (users u JOIN courses c
                ON u.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON com.user_id = u.id"

  # TODO: When course-groups feature is live, un-comment the following.
  #  output_csv "course_group_memberships" "SELECT g.* FROM course_group_memberships g
  #              JOIN (users u JOIN courses c
  #                ON g.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
  #              ON g.canvas_user_id = u.canvas_user_id"
  #
  #  output_csv "course_groups" "SELECT g.* FROM course_groups g
  #              JOIN courses c
  #              ON g.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "whiteboard_users" "SELECT wm.* FROM whiteboard_users wm
              JOIN (whiteboards w JOIN courses c
                ON w.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON wm.whiteboard_id = w.id"

  output_csv "users" "SELECT u.* FROM users u
              JOIN courses c
              ON u.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

# If no source Canvas is specified, select all rows.

else

  output_csv "activities" "SELECT * FROM activities order by id"
  output_csv "activity_types" "SELECT * FROM activity_types"
  output_csv "asset_categories" "SELECT * FROM asset_categories"
  output_csv "asset_users" "SELECT * FROM asset_users"
  output_csv "categories" "SELECT * FROM categories"
  output_csv "comments" "SELECT * FROM comments"
  # TODO: When course-groups feature is live, un-comment the following two lines.
  #  output_csv "course_group_memberships" "SELECT * FROM comments"
  #  output_csv "course_groups" "SELECT * FROM comments"
  output_csv "whiteboard_users" "SELECT * FROM whiteboard_users"
  output_csv "users" "SELECT * FROM users"

fi

# Next, pull data from tables that do contain references to specific Canvas hostnames.

# If the Canvas hostname should be changed, run a replace command on certain columns as part of the query.

if [[ "${replacement_canvas}" ]]; then

  output_csv "assets" "SELECT a.id, a.type, a.url,
                replace(a.download_url, '${source_canvas}', '${replacement_canvas}') as download_url,
                a.title, a.canvas_assignment_id, a.description, a.thumbnail_url, a.image_url, a.mime,
                a.source, a.body, a.likes, a.dislikes, a.views, a.comment_count, a.created_at, a.updated_at,
                a.deleted_at, a.course_id, a.pdf_url, a.preview_status, a.preview_metadata, a.visible
              FROM assets a
              JOIN courses c
              ON a.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "asset_whiteboard_elements" "SELECT awe.uuid,
                replace(awe.element::text, '${source_canvas}', '${replacement_canvas}') as element,
                awe.created_at, awe.updated_at, awe.asset_id, awe.element_asset_id
              FROM asset_whiteboard_elements awe
              JOIN (assets a JOIN courses c
                ON a.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON awe.asset_id = a.id"

  output_csv "courses" "SELECT c.id, c.canvas_course_id, c.enable_upload, c.name,
                replace(c.asset_library_url, '${source_canvas}', '${replacement_canvas}') as asset_library_url,
                replace(c.impact_studio_url, '${source_canvas}', '${replacement_canvas}') as impact_studio_url,
                replace(c.engagement_index_url, '${source_canvas}', '${replacement_canvas}') as engagement_index_url,
                replace(c.whiteboards_url, '${source_canvas}', '${replacement_canvas}') as whiteboards_url,
                '${replacement_canvas}' as canvas_api_domain,
                c.active, c.created_at, c.updated_at, c.enable_daily_notifications, c.enable_weekly_notifications
              FROM courses c
              WHERE c.canvas_api_domain = '${source_canvas}'"

  output_csv "whiteboards" "SELECT w.id, w.title,
                replace(w.thumbnail_url, '${source_canvas}', '${replacement_canvas}') as thumbnail_url,
                replace(w.image_url, '${source_canvas}', '${replacement_canvas}') as image_url,
                w.created_at, w.updated_at, w.course_id, w.deleted_at
              FROM whiteboards w
              JOIN courses c
              ON w.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "whiteboard_elements" "SELECT we.uuid,
                replace(we.element::text, '${source_canvas}', '${replacement_canvas}') as element,
                we.created_at, we.updated_at, we.whiteboard_id, we.asset_id
              FROM whiteboard_elements we
              JOIN (whiteboards w JOIN courses c
                ON w.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON we.whiteboard_id = w.id"

# If the Canvas hostname should not be changed, select all columns without changes.

elif [[ "${source_canvas}" ]]; then

  output_csv "assets" "SELECT a.* FROM assets a
              JOIN courses c
              ON a.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "asset_whiteboard_elements" "SELECT awe.* FROM asset_whiteboard_elements awe
              JOIN (assets a JOIN courses c
                ON a.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON awe.asset_id = a.id"

  output_csv "courses" "SELECT c.* FROM courses c
              WHERE c.canvas_api_domain = '${source_canvas}'"

  # TODO: When course-groups feature is live, un-comment the following.
  #  output_csv "course_groups" "SELECT g.* FROM course_groups g
  #              JOIN courses c
  #              ON g.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"
  #
  #  output_csv "course_group_memberships" "SELECT g.* FROM course_group_memberships g
  #              JOIN courses c
  #              ON g.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "whiteboards" "SELECT w.* FROM whiteboards w
              JOIN courses c
              ON w.course_id = c.id AND c.canvas_api_domain = '${source_canvas}'"

  output_csv "whiteboard_elements" "SELECT we.* FROM whiteboard_elements we
              JOIN (whiteboards w JOIN courses c
                ON w.course_id = c.id AND c.canvas_api_domain = '${source_canvas}')
              ON we.whiteboard_id = w.id"

# If no source Canvas is specified, select all rows.

else

  output_csv "assets" "SELECT * FROM assets"
  output_csv "asset_whiteboard_elements" "SELECT * FROM asset_whiteboard_elements"
  output_csv "courses" "SELECT * FROM courses"
  # TODO: When course-groups feature is live, un-comment the following two lines.
  #  output_csv "course_groups" "SELECT * FROM course_groups"
  #  output_csv "course_group_memberships" "SELECT * FROM course_group_memberships"
  output_csv "whiteboards" "SELECT * FROM whiteboards"
  output_csv "whiteboard_elements" "SELECT * FROM whiteboard_elements"

fi

# If all tables are requested, pull the Canvas table as well.

if [[ "${all_tables}" ]]; then
  output_csv "canvas" "SELECT * FROM canvas"
fi

echo "Done."

exit 0
