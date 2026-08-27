# Bruno API Tests

End-to-end security tests for the fossunited API layer, written in
[Bruno](https://www.usebruno.com/) `.bru` format.

## Prerequisites

1. **Frappe dev server** running at `http://foss.localhost`
2. **Seed data** populated via `development/seed.py`:
   ```bash
   # Frappe Manager
   bench execute development.seed.seed

   # Docker / devcontainer
   docker exec -w /workspace/development/fossu-bench/sites \
     devcontainer-frappe-1 ../env/bin/python /workspace/development/run_seed.py
   ```
3. **Bruno CLI** (`@usebruno/cli`) installed:
   ```bash
   npm install -g @usebruno/cli
   # or use npx (auto-installs)
   ```

## Running tests

From the `bruno-collection/` directory:

```bash
# Run a single folder
npx @usebruno/cli run api/hackathon --env local-development

# Run all test folders
for folder in api/*/; do
  npx @usebruno/cli run "$folder" --env local-development
done
```

Tests also run automatically via the pre-commit hook when Python API files
or `.bru` test files are changed (see `development/run_bruno_tests.sh`).

## Environment variables

Edit `environments/local-development.bru` to match your local seed data.
Key variables:

| Variable | Description | Source |
|---|---|---|
| `base` | Frappe API base URL | site config |
| `hackathon_id` | FOSS Hackathon docname | `MOCK-FOSSIT Hackathon` from seed |
| `hackathon_permalink` | Hackathon permalink slug | seed `HACKATHON_CFG` |
| `rsvp_form_id` | FOSS Event RSVP docname | seed `_create_rsvps` |
| `rsvp_submission_own` | RSVP submission by attendee-1 | seed |
| `rsvp_submission_other` | RSVP submission by attendee-2 | seed |
| `cfp_submission_id` | CFP submission docname | seed `_create_cfps` |
| `newsletter_id` | Newsletter Campaign docname | manual or seed |
| `attendee_email` | Test attendee login | `mock-attendee-1@example.com` |
| `attacker_email` | Second user for ownership tests | `mock-attendee-2@example.com` |
| `chapter_lead_email` | Chapter team member login | `mock-bangalore-lead@example.com` |

All test user passwords default to `password` (set by `development/seed.py`).

### Finding seed data IDs

After running the seed script, look up docnames:

```bash
bench execute frappe.client.get_list \
  --args '{"doctype":"FOSS Hackathon","filters":{"hackathon_name":["like","MOCK-%"]},"fields":["name","hackathon_name","permalink"]}'
```

Or query the database directly:

```sql
SELECT name, hackathon_name, permalink FROM `tabFOSS Hackathon`
  WHERE hackathon_name LIKE 'MOCK-%';
```

## Test folder structure

```
bruno-collection/
├── environments/
│   └── local-development.bru    # env vars for local dev
├── api/
│   ├── hackathon/               # Group 2: field exposure
│   ├── forms/                   # Group 3: auth checks on CFP/forms
│   ├── dashboard/               # Group 4: dashboard field exposure
│   ├── emailing/                # Group 4: campaign field whitelist
│   ├── rsvp/                    # Group 5: mass assignment, ownership
│   └── profile/                 # Group 5: path traversal
├── bruno.json                   # Bruno project config
└── README.md
```

Each folder has a `folder.bru` for shared config (pre-request scripts for
session cookies) and numbered test files that run in sequence.
