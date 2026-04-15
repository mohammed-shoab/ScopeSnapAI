"""
SnapAI — One-Time ONNX Export Script (run on Modal)
Converts YOLOv8 .pt model files → .onnx and uploads to R2.

WHY: ultralytics/PyTorch (~2GB) breaks Railway Hobby builds.
     onnxruntime (~50MB) does not. Same weights, same accuracy.

RUN: modal run scripts/export_to_onnx.py

REQUIRES:
  - modal CLI: pip install modal
  - Authenticated: modal token new
  - R2 env vars in Modal secrets: CLOUDFLARE_R2_ACCOUNT_ID,
    CLOUDFLARE_R2_ACCESS_KEY, CLOUDFLARE_R2_SECRET_KEY, CLOUDFLARE_R2_BUCKET
  - .pt files already uploaded to R2 under models/
    (best_corrosion_v4.pt, scopesnap_multiclass_v1.pt)

OUTPUT: uploads best_corrosion_v4.onnx + scopesnap_multiclass_v1.onnx to R2.
        Railway download_models.py will pull them on next deploy.
"""

import modal

app = modal.App("snapai-onnx-export")

# Use a slim image with ultralytics (only needed for the conversion)
image = modal.Image.debian_slim().pip_install(
    "ultralytics==8.2.0",
    "boto3==1.35.0",
    "onnx>=1.14.0",
    "onnxruntime==1.18.1",
)

PT_MODELS = [
    {
        "pt_key":   "models/best_corrosion_v4.pt",
        "onnx_key": "models/best_corrosion_v4.onnx",
        "name":     "Corrosion v4",
    },
    {
        "pt_key":   "models/scopesnap_multiclass_v1.pt",
        "onnx_key": "models/scopesnap_multiclass_v1.onnx",
        "name":     "Multi-class v1",
    },
]


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("snapai-r2-secrets")],
    timeout=600,
    cpu=4,
)
def export_models():
    import os
    import boto3
    import tempfile
    from pathlib import Path
    from ultralytics import YOLO

    # ── R2 client ─────────────────────────────────────────────────────────────
    account_id  = os.environ["CLOUDFLARE_R2_ACCOUNT_ID"]
    access_key  = os.environ["CLOUDFLARE_R2_ACCESS_KEY"]
    secret_key  = os.environ["CLOUDFLARE_R2_SECRET_KEY"]
    bucket      = os.environ["CLOUDFLARE_R2_BUCKET"]
    endpoint    = f"https://{account_id}.r2.cloudflarestorage.com"

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        for model_cfg in PT_MODELS:
            name     = model_cfg["name"]
            pt_key   = model_cfg["pt_key"]
            onnx_key = model_cfg["onnx_key"]

            pt_path   = tmp / Path(pt_key).name
            onnx_path = tmp / Path(onnx_key).name

            # Download .pt from R2
            print(f"\n[{name}] Downloading {pt_key} from R2...")
            s3.download_file(bucket, pt_key, str(pt_path))
            print(f"[{name}] Downloaded: {pt_path.stat().st_size / 1024 / 1024:.1f} MB")

            # Export to ONNX
            print(f"[{name}] Exporting to ONNX (imgsz=640)...")
            model = YOLO(str(pt_path))
            model.export(
                format="onnx",
                imgsz=640,
                simplify=True,  # Simplify graph for faster inference
                opset=12,       # ONNX opset 12 — compatible with onnxruntime 1.18
            )
            # ultralytics saves as same name with .onnx extension
            exported = pt_path.with_suffix(".onnx")
            if not exported.exists():
                raise FileNotFoundError(f"Export failed — {exported} not found")

            print(f"[{name}] ONNX size: {exported.stat().st_size / 1024 / 1024:.1f} MB")

            # Upload .onnx to R2
            print(f"[{name}] Uploading {onnx_key} to R2...")
            s3.upload_file(str(exported), bucket, onnx_key)
            print(f"[{name}] ✅ Uploaded: {onnx_key}")

    print("\n✅ All models exported and uploaded to R2.")
    print("Railway will pull them on next deploy via scripts/download_models.py")
    print("\nNext step: redeploy Railway — YOLO bounding boxes will be live.")


@app.local_entrypoint()
def main():
    export_models.remote()
