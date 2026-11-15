#!/usr/bin/env bash
# Invoked only by the explicitly authorized production deployment job.
set -euo pipefail
for name in DEPLOY_HOST DEPLOY_PORT DEPLOY_USER DEPLOY_TARGET DEPLOY_KNOWN_HOSTS DEPLOY_SSH_KEY; do
  if [[ -z "${!name:-}" ]]; then echo "::error::Missing deployment configuration: $name"; exit 1; fi
done
[[ "$DEPLOY_PORT" =~ ^[0-9]+$ ]] || { echo 'Invalid deployment port'; exit 1; }
[[ "$DEPLOY_HOST" =~ ^[a-zA-Z0-9.-]+$ && "$DEPLOY_USER" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo 'Invalid deployment host/user'; exit 1; }
[[ "$DEPLOY_TARGET" == '/' || "$DEPLOY_TARGET" == '/var/www/quant/' ]] || { echo 'Deployment target must be the approved quant site directory'; exit 1; }
site_dir="${1:-.site-build/server}"
[[ -f "$site_dir/index.html" && -f "$site_dir/arxiv-data/manifest.json" ]] || { echo 'Incomplete site artifact'; exit 1; }
secret_dir="$(mktemp -d)"
trap 'rm -rf "$secret_dir"' EXIT
umask 077
printf '%s\n' "$DEPLOY_SSH_KEY" > "$secret_dir/key"
printf '%s\n' "$DEPLOY_KNOWN_HOSTS" > "$secret_dir/known_hosts"
unset DEPLOY_SSH_KEY
printf -v ssh_command 'ssh -i %q -p %q -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=%q' "$secret_dir/key" "$DEPLOY_PORT" "$secret_dir/known_hosts"
# Dry run is retained in the job log; scope is restricted to the approved webroot.
rsync -az --delete --delay-updates --itemize-changes --dry-run -e "$ssh_command" "$site_dir/" "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_TARGET"
rsync -az --delete --delay-updates -e "$ssh_command" "$site_dir/" "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_TARGET"
python3 scripts/site/verify_deployment.py "$site_dir" "${SITE_URL:-https://quant.hfthnu.com}"
