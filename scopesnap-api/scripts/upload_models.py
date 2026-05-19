"""
SnapAI — One-Time Model Upload to R2
========================================
Run this ONCE from your local machine to upload the large .pt model files
to Cloudflare R2. After this, Railway will download them on startup.

Usage:
    cd scopesnap-api
    python scripts/upload_models.py

Requires your .env to have:
    R2_ACCOUNT_ID
    R2_ACCESS_KEY_ID
    R2_SECRET_ACCESS_KEY
    R2_BUCKET_NAME

The models are uploaded to:  {R2_BUCKET_NAME}/ai-models/
NOT to the user photos bucket path — kept separate for safety.
"""
import os
import sys
from pathlib import Path

# Load .env from current dir or parent
from dotenv import load_dotenv
load_dotenv()
load_dotenv("../.env")

MODELS_DIR = Path(__file__).parent.parent / "models"
R2_PREFIX = "ai-models"   # folder inside the R2 bucket

# The two large .pt files that can't go in git
MODEL_FILES = [
    "best_corrosion_v4.pt",
    "scopesnap_multiclass_v1.pt",
]


def get_r2_client():
    import boto3
    account_id    = os.environ.get("R2_ACCOUNT_ID", "").strip()
    access_key    = os.environ.get("R2_ACCESS_KEY_ID", "").strip()
    secret_key    = os.environ.get("R2_SECRET_ACCESS_KEY", "").strip()

    if not all([account_id, access_key, secret_key]):
        print("❌ Missing R2 credentials in .env:")
        print("   R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")
        sys.exit(1)

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def upload_models():
    bucket = os.environ.get("R2_BUCKET_NAME", "").strip()
    if not bucket:
        print("❌ R2_BUCKET_NAME not set in .env")
        sys.exit(1)

    client = get_r2_client()

    print(f"\n📦 Uploading AI models to R2 bucket: {bucket}/{R2_PREFIX}/\n")

    for filename in MODEL_FILES:
        local_path = MODELS_DIR / filename
        r2_key = f"{R2_PREFIX}/{filename}"

        if not local_path.exists():
            print(f"⚠️  Skipping {filename} — not found at {local_path}")
            continue

        size_mb = local_path.stat().st_size / (1024 * 1024)
        print(f"⬆️  Uploading {filename} ({size_mb:.1f} MB) → s3://{bucket}/{r2_key}")

        try:
            client.upload_file(
                str(local_path),
                bucket,
                r2_key,
                ExtraArgs={"ContentType": "application/octet-stream"},
            )
            print(f"✅ {filename} uploaded successfully")
        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")
            sys.exit(1)

    print("\n✅ All model files uploaded to R2.")
    print(f"   Railway will now download them automatically on container startup.")
    print(f"   R2 path: {bucket}/{R2_PREFIX}/")


if __name__ == "__main__":
    upload_models()
