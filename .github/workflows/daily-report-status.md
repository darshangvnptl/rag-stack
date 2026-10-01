---
name: Daily Report Status
description: Create a daily, evidence-based summary of repository activity.
intent: Give maintainers a concise, evidence-based view of repository activity over the last 24 hours.
on:
  schedule: daily
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  copilot-requests: write
tools:
  github:
    mode: gh-proxy
    toolsets: [repos, issues]
steps:
  - name: Collect repository activity
    env:
      GH_TOKEN: ${{ github.token }}
      REPOSITORY: ${{ github.repository }}
    run: |
      set -euo pipefail

      mkdir -p /tmp/gh-aw/data
      WINDOW_END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      WINDOW_START="$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)"

      gh api "repos/${REPOSITORY}/commits?since=${WINDOW_START}&until=${WINDOW_END}&per_page=100" \
        --jq '[.[] | {
          sha: .sha[0:7],
          author: (.author.login // .commit.author.name),
          date: .commit.author.date,
          message: (.commit.message | split("\n")[0])
        }]' > /tmp/gh-aw/data/commits.json

      gh api "repos/${REPOSITORY}/issues?state=all&since=${WINDOW_START}&per_page=100" \
        | jq --arg window_end "$WINDOW_END" '[
            .[]
            | select(has("pull_request") | not)
            | select(.updated_at <= $window_end)
            | {
                number,
                title,
                state,
                author: (.user.login // "unknown"),
                created_at,
                updated_at,
                labels: [.labels[].name]
              }
          ]' > /tmp/gh-aw/data/issues.json

      jq -n \
        --arg repository "$REPOSITORY" \
        --arg window_start "$WINDOW_START" \
        --arg window_end "$WINDOW_END" \
        --slurpfile commits /tmp/gh-aw/data/commits.json \
        --slurpfile issues /tmp/gh-aw/data/issues.json \
        '{
          repository: $repository,
          window_start_utc: $window_start,
          window_end_utc: $window_end,
          commits: $commits[0],
          issues: $issues[0]
        }' > /tmp/gh-aw/data/activity.json
safe-outputs:
  create-issue:
    title-prefix: "Daily Repository Activity Report: "
    max: 1
strict: true
---

# Daily Report Status

## Task

Read `/tmp/gh-aw/data/activity.json` and create one concise daily activity report issue for its UTC 24-hour window. Summarize commits and issue activity, grouping issues by state and highlighting notable changes without inventing context. Include the repository, exact window, and the stable deduplication key `daily-report:<UTC date of window_end_utc>` in the report body.

Before creating an issue, search all issues (open and closed) for that key. If a report with the key already exists, call `noop` and do not create a duplicate. If there were no commits or issue updates in the window, call `noop` with the evaluated UTC window. If the activity data is missing or invalid, call `noop` rather than guessing.

Use a meaningful title suffix with the UTC date, and create the report only through the configured `create-issue` safe output. Format the body with a short summary, then `###` sections for commits and issue activity; use links for referenced issues when available. Do not include pull-request activity because this workflow does not request pull-request read permission.

## Safe Outputs

- Use `create-issue` for the daily report and no other write mechanism.
- Call `noop` with a short reason for duplicates, empty windows, or unusable evidence.
