#!/usr/bin/env bash
set -euo pipefail
# promote-to-prod.sh — cherry-pick specific files from staging onto main, then push.
# Usage: ./scripts/promote-to-prod.sh path/to/file1 path/to/file2 ...
# Example: ./scripts/promote-to-prod.sh scopesnap-web/components/StagingBanner.tsx

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 path/to/file1 [path/to/file2 ...]"
  exit 1
fi

FILES=("$@")

git fetch origin

# Switch to main and pull latest
git checkout main && git pull origin main

# Overlay specified files from staging
for f in "${FILES[@]}"; do
  git checkout origin/staging -- "$f"
  echo "Overlaid: $f"
done

# Truncation guard — .ts/.tsx files must have at least 5 lines
for f in "${FILES[@]}"; do
  case "$f" in
    *.ts|*.tsx)
      LINES=$(wc -l < "$f")
      if [ "$LINES" -lt 5 ]; then
        echo "ERROR: $f looks truncated ($LINES lines). Aborting."
        exit 1
      fi
      ;;
  esac
done

git add "${FILES[@]}"

read -rp "Commit message: " MSG
git commit -m "$MSG"
git push origin main

echo "Done. Files promoted to main."
