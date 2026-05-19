"""
SnapAI — One-Time Model Upload to GitHub Releases
=====================================================
Uploads the large YOLO .pt model files to a GitHub Release.
After this, Railway downloads them automatically on every deploy.

HOW TO RUN (once, from your PC):
    cd scopesnap-api
    python scripts/upload_models_github.py

Requirements: Python 3.8+ with 'requests' package
    pip install requests

What it does:
    1. Creates a GitHub Release tagged 'ai-models-v1' (if not already there)
    2. Uploads best_corrosion_v4.pt     (~149 MB)
    3. Uploads scopesnap_multiclass_v1.pt (~50 MB)

After upload, Railway's start.sh will automatically download these
files from GitHub on every container startup (via download_models.py).
"""
import os
import sys
import time
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # set via env var — never hardcode
REPO         = "mohammed-shoab/ScopeSnapAI"
RELEASE_TAG  = "ai-models-v1"
RELEASE_NAME = "AI Model Files — YOLO v4 + Multi-class v1"
RELEASE_BODY = (
    "Large AI model files for the SnapAI Dual-Track Cascade.\n\n"
    "- best_corrosion_v4.pt — 85% mAP50, trained on corrosion detection\n"
    "- scopesnap_multiclass_v1.pt — 8-class HVAC fault detector\n\n"
    "These files are automatically downloaded by the Railway backend on startup.\n"
    "Do NOT delete this release — Railway depends on it."
)

MODELS_DIR = Path(__file__).parent.parent / "models"
MODEL_FILES = [
    "best_corrosion_v4.pt",
    "scopesnap_multiclass_v1.pt",
]

API_BASE   = "https://api.github.com"
UPLOAD_URL = "https://uploads.github.com"

# ── Helpers ────────────────────────────────────────────────────────────────────

def headers(extra=None):
    h = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    if extra:
        h.update(extra)
    return h


def get_or_create_release() -> dict:
    import requests

    # Check if release exists
    r = requests.get(
        f"{API_BASE}/repos/{REPO}/releases/tags/{RELEASE_TAG}",
        headers=headers(),
        timeout=30,
    )
    if r.status_code == 200:
        release = r.json()
        print(f"✅ Release '{RELEASE_TAG}' already exists (id={release['id']})")
        return release

    # Create it
    print(f"📦 Creating GitHub Release '{RELEASE_TAG}'...")
    r = requests.post(
        f"{API_BASE}/repos/{REPO}/releases",
        headers=headers(),
        json={
            "tag_name": RELEASE_TAG,
            "name": RELEASE_NAME,
            "body": RELEASE_BODY,
            "draft": False,
            "prerelease": False,
        },
        timeout=30,
    )
    if r.status_code not in (200, 201):
        print(f"❌ Failed to create release: {r.status_code} {r.text}")
        sys.exit(1)

    release = r.json()
    print(f"✅ Release created (id={release['id']})")
    return release


def asset_already_uploaded(release: dict, filename: str) -> bool:
    for asset in release.get("assets", []):
        if asset["name"] == filename:
            print(f"✅ {filename} already uploaded ({asset['size'] / 1024 / 1024:.1f} MB) — skipping")
            return True
    return False


def upload_asset(release_id: int, file_path: Path):
    import requests

    filename = file_path.name
    size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"\n⬆️  Uploading {filename} ({size_mb:.1f} MB)...")
    print("   This may take several minutes on slow connections. Please wait...")

    upload_url = f"{UPLOAD_URL}/repos/{REPO}/releases/{release_id}/assets?name={filename}"

    with open(file_path, "rb") as f:
        start = time.time()
        r = requests.post(
            upload_url,
            headers=headers({"Content-Type": "application/octet-stream"}),
            data=f,
            timeout=600,  # 10 min timeout for large files
        )
    elapsed = time.time() - start

    if r.status_code not in (200, 201):
        print(f"❌ Upload failed: {r.status_code} {r.text[:500]}")
        sys.exit(1)

    asset = r.json()
    print(f"✅ {filename} uploaded in {elapsed:.0f}s → {asset['browser_download_url']}")
    return asset["browser_download_url"]


def main():
    try:
        import requests
    except ImportError:
        print("❌ 'requests' package not installed.")
        print("   Run: pip install requests")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  SnapAI — AI Model Upload to GitHub Releases")
    print("=" * 60)

    # Check model files exist
    missing = [f for f in MODEL_FILES if not (MODELS_DIR / f).exists()]
    if missing:
        print(f"❌ Model files not found in {MODELS_DIR}:")
        for f in missing:
            print(f"   Missing: {f}")
        sys.exit(1)

    print(f"\n📁 Models found in: {MODELS_DIR}")
    for f in MODEL_FILES:
        size_mb = (MODELS_DIR / f).stat().st_size / (1024 * 1024)
        print(f"   ✓ {f} ({size_mb:.1f} MB)")

    # Get or create release
    release = get_or_create_release()
    release_id = release["id"]

    # Upload each model file
    download_urls = {}
    for filename in MODEL_FILES:
        file_path = MODELS_DIR / filename
        if asset_already_uploaded(release, filename):
            # Already there — build the URL
            for asset in release["assets"]:
                if asset["name"] == filename:
                    download_urls[filename] = asset["browser_download_url"]
            continue
        url = upload_asset(release_id, file_path)
        download_urls[filename] = url

    print("\n" + "=" * 60)
    print("✅ ALL MODELS UPLOADED SUCCESSFULLY")
    print("=" * 60)
    print("\nDownload URLs (Railway will use these automatically):")
    for filename, url in download_urls.items():
        print(f"  {filename}:\n    {url}")

    print("\n✅ Next step: push your code to GitHub → Railway auto-deploys")
    print("   Railway will download models from GitHub on each container start.")


if __name__ == "__main__":
    main()
