#!/bin/bash
# ── SnapAI — Daily Database Backup to R2 ─────────────────────────────────────
# Run as a Railway cron job: 0 2 * * * (2am UTC daily)
#
# Required env vars (all already set in Railway):
#   DATABASE_URL               PostgreSQL connection string
#   CLOUDFLARE_R2_ACCESS_KEY   R2 access key ID
#   CLOUDFLARE_R2_SECRET_KEY   R2 secret access key
#   CLOUDFLARE_R2_ACCOUNT_ID   Cloudflare account ID
#   CLOUDFLARE_R2_BUCKET       R2 bucket name
#
# To run manually on Railway: railway run bash scripts/backup_db.sh

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/tmp/snapai_backup_${DATE}.sql.gz"
BUCKET="${CLOUDFLARE_R2_BUCKET:-snapai-uploads}"
R2_KEY="backups/snapai_backup_${DATE}.sql.gz"
R2_ENDPOINT="https://${CLOUDFLARE_R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

echo "=================================================="
echo "  SnapAI DB Backup — $(date)"
echo "=================================================="

# Dump and compress
echo "Dumping PostgreSQL database..."
pg_dump "${DATABASE_URL}" | gzip > "${BACKUP_FILE}"
SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
echo "  Backup size: ${SIZE}"

# Upload to R2 using AWS CLI (boto3 equivalent via env vars)
echo "Uploading to R2: s3://${BUCKET}/${R2_KEY}"
AWS_ACCESS_KEY_ID="${CLOUDFLARE_R2_ACCESS_KEY}" \
AWS_SECRET_ACCESS_KEY="${CLOUDFLARE_R2_SECRET_KEY}" \
aws s3 cp "${BACKUP_FILE}" "s3://${BUCKET}/${R2_KEY}" \
  --endpoint-url "${R2_ENDPOINT}" \
  --region auto

echo "  Upload complete: ${R2_KEY}"

# Clean up local temp file
rm -f "${BACKUP_FILE}"

# Delete backups older than 30 days from R2
echo "Pruning backups older than 30 days..."
CUTOFF=$(date -d "30 days ago" +%Y%m%d 2>/dev/null || date -v-30d +%Y%m%d)
AWS_ACCESS_KEY_ID="${CLOUDFLARE_R2_ACCESS_KEY}" \
AWS_SECRET_ACCESS_KEY="${CLOUDFLARE_R2_SECRET_KEY}" \
aws s3 ls "s3://${BUCKET}/backups/" \
  --endpoint-url "${R2_ENDPOINT}" \
  --region auto | while read -r line; do
    FILE_DATE=$(echo "$line" | grep -oP '\d{8}' | head -1)
    FILE_NAME=$(echo "$line" | awk '{print $4}')
    if [[ -n "$FILE_DATE" && "$FILE_DATE" < "$CUTOFF" ]]; then
        echo "  Deleting old backup: ${FILE_NAME}"
        AWS_ACCESS_KEY_ID="${CLOUDFLARE_R2_ACCESS_KEY}" \
        AWS_SECRET_ACCESS_KEY="${CLOUDFLARE_R2_SECRET_KEY}" \
        aws s3 rm "s3://${BUCKET}/backups/${FILE_NAME}" \
          --endpoint-url "${R2_ENDPOINT}" \
          --region auto
    fi
done

echo "=================================================="
echo "  Backup complete: ${R2_KEY}"
echo "=================================================="
