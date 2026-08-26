#!/usr/bin/env bash
set -euo pipefail

# Maps changed Python API files and Bruno test files to the Bruno folders
# that need to run. Skips gracefully if the Frappe server is unreachable.

BRUNO_DIR="bruno-collection"
ENV="local-development"
BASE_URL="http://foss.localhost/api"

# Python module → Bruno test folder mapping
declare -A API_MAP=(
  ["fossunited/api/tickets.py"]="api/tickets"
  ["fossunited/api/checkins.py"]="api/checkins"
  ["fossunited/api/hackathon.py"]="api/hackathon"
  ["fossunited/api/cfp.py"]="api/cfp"
  ["fossunited/api/proposal.py"]="api/proposal"
  ["fossunited/api/rsvp.py"]="api/rsvp"
  ["fossunited/api/dashboard.py"]="api/dashboard"
  ["fossunited/api/emailing.py"]="api/emailing"
  ["fossunited/api/profile.py"]="api/profile"
  ["fossunited/api/schedule.py"]="api/schedule"
)

FOLDERS_TO_RUN=()

for file in "$@"; do
  # If a Python API file changed, queue its Bruno folder
  if [[ -v "API_MAP[$file]" ]]; then
    FOLDERS_TO_RUN+=("${API_MAP[$file]}")
  fi

  # If a Bruno test file changed, queue its parent folder
  if [[ "$file" == "$BRUNO_DIR/"* && "$file" == *.yml ]]; then
    folder=$(dirname "$file" | sed "s|^$BRUNO_DIR/||")
    if [[ "$folder" != "environments" && "$folder" != "." ]]; then
      FOLDERS_TO_RUN+=("$folder")
    fi
  fi
done

# Deduplicate
readarray -t FOLDERS_TO_RUN < <(printf '%s\n' "${FOLDERS_TO_RUN[@]}" | sort -u)

if [[ ${#FOLDERS_TO_RUN[@]} -eq 0 ]]; then
  exit 0
fi

# Check if Frappe server is reachable
if ! curl -sf --max-time 3 "$BASE_URL/method/frappe.ping" > /dev/null 2>&1; then
  echo "⚠  Frappe server not reachable at $BASE_URL — skipping Bruno tests"
  echo "   Start the server and run manually: npx @usebruno/cli run bruno-collection/<folder> --env $ENV"
  exit 0
fi

FAILED=0
for folder in "${FOLDERS_TO_RUN[@]}"; do
  folder_path="$BRUNO_DIR/$folder"
  if [[ ! -d "$folder_path" ]]; then
    continue
  fi
  echo "▶ Running Bruno tests: $folder"
  if ! npx @usebruno/cli run "$folder_path" --env "$ENV"; then
    echo "✗ FAILED: $folder"
    FAILED=1
  fi
done

if [[ $FAILED -ne 0 ]]; then
  echo ""
  echo "Bruno tests failed. Fix the issues above before committing."
  exit 1
fi

echo "✓ All Bruno tests passed"
