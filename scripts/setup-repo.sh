#!/usr/bin/env bash
# Maintainer script: creates the public repo and applies protections so the owner
# must approve CI runs and merges. Requires: gh authenticated with admin rights.
# Usage: scripts/setup-repo.sh <owner>/pr-bar
set -euo pipefail
REPO="${1:?usage: setup-repo.sh <owner>/<repo>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --source "$ROOT" --remote origin \
    --description "Menu bar tracker for your GitHub pull requests (SwiftBar + gh)"
  git -C "$ROOT" push -u origin HEAD
fi

# Require owner approval before workflows run for ALL outside contributors.
gh api -X PUT "repos/$REPO/actions/permissions/fork-pr-contributor-approval" \
  -f approval_policy=all_external_contributors

# Workflow tokens are read-only and cannot approve PRs.
gh api -X PUT "repos/$REPO/actions/permissions/workflow" \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false

# Protect main: PR + code-owner review required, CI must pass, admins included, no force pushes.
gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["test"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": true,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
echo "Protections applied to $REPO."
