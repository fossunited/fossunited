#!/usr/bin/env bash
set -euo pipefail

# Maps changed Python API files and Bruno test files to the Bruno folders
# that need to run. Skips gracefully if the Frappe server is unreachable.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRUNO_DIR="bruno-collection"
ENV="local-development"
BASE_URL="http://foss.localhost/api"

# Resolve how to invoke `bru`:
#   1. Already on PATH (e.g. installed globally via distro package manager, or via nix).
#   2. Already installed locally under node_modules/.bin (yarn/npm install already ran).
#   3. Not installed yet: install it via whichever of yarn/npm is available.
resolve_bru() {
  if command -v bru >/dev/null 2>&1; then
    command -v bru
    return
  fi

  if [[ -x "$ROOT_DIR/node_modules/.bin/bru" ]]; then
    echo "$ROOT_DIR/node_modules/.bin/bru"
    return
  fi

  if command -v yarn >/dev/null 2>&1; then
    echo "Bruno CLI not found — installing dependencies with yarn..." >&2
    (cd "$ROOT_DIR" && yarn install --silent)
  elif command -v npm >/dev/null 2>&1; then
    echo "Bruno CLI not found — installing dependencies with npm..." >&2
    (cd "$ROOT_DIR" && npm install --silent)
  else
    return
  fi

  if [[ -x "$ROOT_DIR/node_modules/.bin/bru" ]]; then
    echo "$ROOT_DIR/node_modules/.bin/bru"
  fi
}


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
  if [[ "$file" == "$BRUNO_DIR/"* && ( "$file" == *.bru || "$file" == *.yml ) ]]; then
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
  echo "   Start the server and run manually: bru run bruno-collection/<folder> --env $ENV"
  exit 0
fi

BRU_BIN="$(resolve_bru)"
if [[ -z "$BRU_BIN" ]]; then
  echo "⚠  Bruno CLI (bru) not found, and neither yarn nor npm is available — skipping Bruno tests"
  exit 0
fi

FAILED=0
for folder in "${FOLDERS_TO_RUN[@]}"; do
  folder_path="$BRUNO_DIR/$folder"
  if [[ ! -d "$folder_path" ]]; then
    continue
  fi
  echo "▶ Running Bruno tests: $folder"
  if ! (cd "$BRUNO_DIR" && "$BRU_BIN" run "$folder" --env "$ENV"); then
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
