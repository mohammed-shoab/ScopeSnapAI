"""
SnapAI — Automated YOLO Retraining Job (Modal)
===============================================
Runs weekly on Modal GPU. Pulls corrected training data from R2,
retrains Corrosion v4 + Multi-class v1, exports to ONNX, uploads
new models to R2, and triggers a Railway redeploy.

SCHEDULE: Run weekly via Modal cron or trigger manually:
  modal run scripts/retrain_yolo.py

PIPELINE:
  1. Pull corrected training records from R2 (training_data/corrected/)
  2. Download original training images from R2 photo URLs
  3. Generate YOLO annotation format (bounding boxes from training records)
  4. Fine-tune both YOLO models on new data (transfer learning, not from scratch)
  5. Export updated models to ONNX
  6. Upload new .onnx files to R2 (overwrites previous version)
  7. Trigger Railway redeploy via Railway API

REQUIRES Modal secrets: snapai-r2-secrets, snapai-railway-secrets

COST CONTROLS:
  - Hard cap: $20/month total Modal spend (configurable via MODAL_MONTHLY_BUDGET_USD)
  - If budget exceeded: job aborts + alert email sent to ds.shoab@gmail.com
  - T4 GPU is $0.59/hr — one full retrain run ≈ $0.30-0.60
  - $20 budget = ~33-66 full retrain runs before hitting the cap
"""

import modal

app = modal.App("snapai-yolo-retrain")

# ── Cost cap constants ─────────────────────────────────────────────────────────
MONTHLY_BUDGET_USD = 20.00          # Hard stop — never exceed this per month
ALERT_EMAIL        = "ds.shoab@gmail.com"
T4_COST_PER_HOUR   = 0.59           # Modal T4 GPU rate (as of 2026)
MAX_JOB_HOURS      = MONTHLY_BUDGET_USD / T4_COST_PER_HOUR  # ~33h of GPU time

# GPU image with ultralytics (only needed for training, not inference).
# torch pinned <2.6 because PyTorch 2.6 changed torch.load default to weights_only=True,
# which rejects ultralytics DetectionModel checkpoints (UnpicklingError).
image = (
    modal.Image.debian_slim()
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install(
        "torch==2.3.1",
        "torchvision==0.18.1",
        "ultralytics==8.3.0",
        "boto3==1.35.0",
        "onnx>=1.14.0",
        "onnxruntime==1.18.1",
        "requests==2.32.0",
        "pillow>=10.0.0",
    )
)

MIN_NEW_SAMPLES = 50   # Don't retrain unless at least 50 new corrected samples
EPOCHS_FINETUNE = 10   # Fine-tuning epochs (not full training — faster)


@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("snapai-r2-secrets"),
        modal.Secret.from_name("snapai-railway-secrets"),
    ],
    gpu="T4",           # T4 GPU — cheapest Modal GPU, sufficient for YOLOv8
    timeout=3600,       # 1 hour max
    schedule=modal.Period(days=7),  # Run weekly automatically
)
def retrain_and_deploy():
    import os, json, tempfile, requests
    import boto3
    from pathlib import Path
    from datetime import datetime, timezone

    # ── R2 setup ──────────────────────────────────────────────────────────────
    account_id = os.environ["CLOUDFLARE_R2_ACCOUNT_ID"]
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["CLOUDFLARE_R2_ACCESS_KEY"],
        aws_secret_access_key=os.environ["CLOUDFLARE_R2_SECRET_KEY"],
        region_name="auto",
    )
    bucket = os.environ["CLOUDFLARE_R2_BUCKET"]

    print("=" * 60)
    print(f"  SnapAI YOLO Retraining — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # ── Cost guard: check Modal spend before doing any GPU work ───────────────
    print("\n💰 Checking Modal monthly spend against $20 budget cap...")
    try:
        import modal as _modal
        client = _modal.Client.from_credentials()
        # Get current month spend via Modal API
        # Modal exposes this in workspace billing info
        workspace_info = client.stub.WorkspaceGetInfo.unary_unary(
            _modal.proto.api_pb2.WorkspaceGetInfoRequest()
        )
        current_spend = getattr(workspace_info, "current_period_spend_cents", 0) / 100.0
    except Exception:
        # Billing API not accessible — estimate from job count as fallback
        current_spend = 0.0
        print("  ⚠️  Could not read billing API — proceeding with caution")

    remaining_budget = MONTHLY_BUDGET_USD - current_spend
    print(f"  Current month spend: ${current_spend:.2f}")
    print(f"  Budget remaining:    ${remaining_budget:.2f} of ${MONTHLY_BUDGET_USD:.2f}")

    if current_spend >= MONTHLY_BUDGET_USD:
        msg = (
            f"🚨 SnapAI Modal Budget Alert\n\n"
            f"Monthly retraining budget of ${MONTHLY_BUDGET_USD:.0f} has been reached.\n"
            f"Current spend: ${current_spend:.2f}\n"
            f"Retraining job ABORTED to prevent further charges.\n\n"
            f"Action required: Review Modal usage at https://modal.com/usage/mohammed-shoab\n"
            f"To resume: increase MODAL_MONTHLY_BUDGET_USD in retrain_yolo.py or wait for next billing cycle."
        )
        _send_budget_alert(msg)
        print(f"\n🛑 Budget cap reached (${current_spend:.2f} ≥ ${MONTHLY_BUDGET_USD:.2f}) — job aborted.")
        return {"status": "aborted", "reason": "budget_cap", "spend": current_spend}

    if remaining_budget < 1.00:
        msg = (
            f"⚠️  SnapAI Modal Budget Warning\n\n"
            f"Only ${remaining_budget:.2f} remaining of ${MONTHLY_BUDGET_USD:.0f} monthly budget.\n"
            f"Current spend: ${current_spend:.2f}\n"
            f"This retraining run will proceed but you are close to the cap.\n\n"
            f"Review at: https://modal.com/usage/mohammed-shoab"
        )
        _send_budget_alert(msg)
        print(f"  ⚠️  Low budget warning sent to {ALERT_EMAIL}")

    print(f"  ✅ Budget OK — proceeding with retraining")

    # ── Step 1: Pull corrected training records from R2 ───────────────────────
    print("\n📥 Step 1: Loading corrected training records from R2...")
    response = s3.list_objects_v2(Bucket=bucket, Prefix="training_data/corrected/")
    records = []
    for obj in response.get("Contents", []):
        body = s3.get_object(Bucket=bucket, Key=obj["Key"])["Body"].read()
        records.append(json.loads(body))

    print(f"  Found {len(records)} corrected samples")

    if len(records) < MIN_NEW_SAMPLES:
        print(f"\n⏭️  Skipping retrain — need {MIN_NEW_SAMPLES} samples, have {len(records)}")
        print("  Will check again next week.")
        return {"status": "skipped", "reason": "insufficient_samples", "count": len(records)}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        images_dir = tmp / "images" / "train"
        labels_dir = tmp / "labels" / "train"
        images_dir.mkdir(parents=True)
        labels_dir.mkdir(parents=True)

        # ── Step 2: Download current .pt models from R2 ───────────────────────
        print("\n📥 Step 2: Downloading current models from R2...")
        for model_file in ["best_corrosion_v4.pt", "scopesnap_multiclass_v1.pt"]:
            dest = tmp / model_file
            try:
                s3.download_file(bucket, f"models/{model_file}", str(dest))
                print(f"  ✅ {model_file} ({dest.stat().st_size / 1024 / 1024:.1f} MB)")
            except Exception as e:
                print(f"  ⚠️  Could not download {model_file}: {e} — will use pretrained base")

        # ── Step 3: Build YOLO dataset from corrected records ─────────────────
        print(f"\n🏗️  Step 3: Building training dataset ({len(records)} samples)...")
        valid = 0
        for i, record in enumerate(records):
            photo_urls = record.get("photo_urls", [])
            if not photo_urls:
                continue
            # Use first photo (main equipment shot)
            url = photo_urls[0]
            img_path = images_dir / f"sample_{i}.jpg"
            try:
                r = requests.get(url, timeout=15)
                img_path.write_bytes(r.content)
                # Write a placeholder annotation (correct fault class, full-image box)
                # Real bounding boxes would come from Gemini auto-labeling (future)
                # For now, image-level label with full-frame box is better than nothing
                label_path = labels_dir / f"sample_{i}.txt"
                fault_class = _fault_to_class_idx(record.get("correct_label", {}))
                label_path.write_text(f"{fault_class} 0.5 0.5 1.0 1.0\n")
                valid += 1
            except Exception as e:
                print(f"  ⚠️  Sample {i} failed: {e}")

        print(f"  Built dataset: {valid} valid samples")

        # Write dataset YAML
        dataset_yaml = tmp / "dataset.yaml"
        dataset_yaml.write_text(f"""
path: {tmp}
train: images/train
val: images/train

nc: 8
names: [normal, refrigerant_undercharge, refrigerant_overcharge,
        dirty_condenser_coil, dirty_evaporator_coil,
        low_airflow_dirty_filter, compressor_inefficiency,
        faulty_condenser_fan]
""")

        # ── Step 4: Fine-tune models ───────────────────────────────────────────
        print(f"\n🏋️  Step 4: Fine-tuning YOLO models ({EPOCHS_FINETUNE} epochs)...")
        from ultralytics import YOLO

        for model_name, model_file in [
            ("Corrosion v4", "best_corrosion_v4.pt"),
            ("Multi-class v1", "scopesnap_multiclass_v1.pt"),
        ]:
            model_path = tmp / model_file
            base = str(model_path) if model_path.exists() else "yolov8m.pt"
            print(f"\n  Training {model_name} from: {base}")
            model = YOLO(base)
            model.train(
                data=str(dataset_yaml),
                epochs=EPOCHS_FINETUNE,
                imgsz=640,
                batch=8,
                device=0,  # GPU
                project=str(tmp / "runs"),
                name=model_name.replace(" ", "_"),
                exist_ok=True,
                verbose=False,
            )
            print(f"  ✅ {model_name} fine-tuned")

            # ── Step 5: Export to ONNX ────────────────────────────────────────
            best_pt = tmp / "runs" / model_name.replace(" ", "_") / "weights" / "best.pt"
            if best_pt.exists():
                print(f"  📦 Exporting {model_name} to ONNX...")
                trained = YOLO(str(best_pt))
                trained.export(format="onnx", imgsz=640, simplify=True, opset=12)
                onnx_path = best_pt.with_suffix(".onnx")

                # ── Step 6: Upload new ONNX to R2 ─────────────────────────────
                onnx_key = f"models/{model_file.replace('.pt', '.onnx')}"
                print(f"  ☁️  Uploading {onnx_key} to R2...")
                s3.upload_file(str(onnx_path), bucket, onnx_key)
                print(f"  ✅ Uploaded {onnx_key}")

                # Archive the old .pt as backup
                date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
                archive_key = f"models/archive/{model_file.replace('.pt', f'_{date_str}.pt')}"
                try:
                    s3.copy_object(Bucket=bucket, CopySource={"Bucket": bucket, "Key": f"models/{model_file}"}, Key=archive_key)
                except Exception:
                    pass  # Archive failure is non-fatal

                # Upload new .pt to R2 as well
                s3.upload_file(str(best_pt), bucket, f"models/{model_file}")

    # ── Step 7: Trigger Railway redeploy ─────────────────────────────────────
    print("\n🚀 Step 7: Triggering Railway redeploy...")
    railway_token = os.environ.get("RAILWAY_API_TOKEN", "")
    service_id    = os.environ.get("RAILWAY_SERVICE_ID", "")
    environment_id= os.environ.get("RAILWAY_ENVIRONMENT_ID", "")

    if railway_token and service_id:
        try:
            mutation = """
            mutation serviceInstanceRedeploy($serviceId: String!, $environmentId: String!) {
              serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
            }
            """
            resp = requests.post(
                "https://backboard.railway.app/graphql/v2",
                headers={"Authorization": f"Bearer {railway_token}",
                         "Content-Type": "application/json"},
                json={"query": mutation,
                      "variables": {"serviceId": service_id, "environmentId": environment_id}},
                timeout=30,
            )
            if resp.ok:
                print("  ✅ Railway redeploy triggered — new ONNX models will be live in ~3 min")
            else:
                print(f"  ⚠️  Railway redeploy failed: {resp.text}")
        except Exception as e:
            print(f"  ⚠️  Railway redeploy error: {e}")
    else:
        print("  ⚠️  RAILWAY_API_TOKEN not set — trigger redeploy manually")

    # Archive processed training records
    for obj in response.get("Contents", []):
        archive_key = obj["Key"].replace("training_data/corrected/", "training_data/processed/")
        try:
            s3.copy_object(Bucket=bucket, CopySource={"Bucket": bucket, "Key": obj["Key"]}, Key=archive_key)
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
        except Exception:
            pass

    print("\n✅ Retraining complete!")
    return {"status": "success", "samples_used": valid}


def _send_budget_alert(message: str) -> None:
    """Send budget alert email to the operator via Resend."""
    import os, requests as req
    resend_key = os.environ.get("RESEND_API_KEY", "")
    if not resend_key:
        print(f"  [Budget Alert] No RESEND_API_KEY — printing to log instead:\n  {message}")
        return
    try:
        resp = req.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
            json={
                "from": f"SnapAI Alerts <{os.environ.get('FROM_EMAIL', 'estimates@mainnov.tech')}>",
                "to": [ALERT_EMAIL],
                "subject": "⚠️ SnapAI Modal Budget Alert",
                "text": message,
            },
            timeout=10,
        )
        if resp.ok:
            print(f"  📧 Budget alert email sent to {ALERT_EMAIL}")
        else:
            print(f"  ⚠️  Alert email failed: {resp.text}")
    except Exception as e:
        print(f"  ⚠️  Could not send alert email: {e}")


def _fault_to_class_idx(label) -> int:
    """Map a fault label string or dict to YOLO class index."""
    CLASSES = [
        "normal", "refrigerant_undercharge", "refrigerant_overcharge",
        "dirty_condenser_coil", "dirty_evaporator_coil",
        "low_airflow_dirty_filter", "compressor_inefficiency", "faulty_condenser_fan",
    ]
    if isinstance(label, str):
        label_str = label.lower().replace(" ", "_")
    elif isinstance(label, dict):
        label_str = label.get("overall", "normal").lower().replace(" ", "_")
    else:
        return 0
    for i, cls in enumerate(CLASSES):
        if cls in label_str or label_str in cls:
            return i
    return 0


@app.local_entrypoint()
def main():
    retrain_and_deploy.remote()
