"""
SnapAI — PDF Layout Sandbox
===========================
Run this script to generate a sample estimate PDF.
Iterate on the layout here until it looks perfect, then paste the
draw_estimate() function back into scopesnap-api/services/pdf_generator.py.

Usage:
    python sample_estimate.py
    → opens estimate_preview.pdf in the same folder

The sample data below matches rpt-2246 (the real estimate Shoab reviewed).
"""

import sys, os

# ── Make sure the api service is importable ──────────────────────────────────
# Adjust this path if you run from a different directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.join(SCRIPT_DIR, "..", "scopesnap-api")
sys.path.insert(0, API_DIR)

from services.pdf_generator import generate_contractor_pdf

# ── Sample data matching rpt-2246 ────────────────────────────────────────────
SAMPLE_ESTIMATE = {
    "report_short_id": "rpt-2246",
    "photo_url": "",   # leave blank for local testing (no network call)

    "company": {
        "name": "SnapAI",
        "phone": "",
        "license_number": "",
        "logo_url": "",
    },

    "property": {
        "customer_name": "Homeowner",
        "address_line1": "",
        "city": "",
        "state": "",
        "zip": "",
    },

    "equipment": {
        "brand": "",
        "model_number": "",
        "install_year": "",
    },

    "issues": [],   # no issues detected on this working AC

    "options": [
        {
            "tier": "good",
            "name": "Preventive Maintenance",
            "description": "Addresses the immediate issue at the lowest cost.",
            "total": 189,
            "subtotal": 140,
            "markup_percent": 35,
            "five_year_total": 2589,
            "energy_savings": None,
            "line_items": [
                {"description": "Parts and materials (Preventive Maintenance)", "total": 20},
                {"description": "Labor (1.0 hours @ $95.0/hr)",                "total": 95},
                {"description": "Filter",                                       "total": 25},
            ],
        },
        {
            "tier": "better",
            "name": "Diagnostic & Repair",
            "description": "Best value - resolves the root cause with durable parts.",
            "total": 526,
            "subtotal": 390,
            "markup_percent": 35,
            "five_year_total": 2926,
            "energy_savings": None,
            "line_items": [
                {"description": "Parts and materials (Diagnostic & Repair)", "total": 200},
                {"description": "Labor (2.0 hours @ $95.0/hr)",             "total": 190},
            ],
        },
        {
            "tier": "best",
            "name": "New System Installation",
            "description": "Long-term solution with maximum efficiency and warranty.",
            "total": 9572,
            "subtotal": 7090,
            "markup_percent": 35,
            "five_year_total": 11972,
            "energy_savings": None,
            "line_items": [
                {"description": "Parts and materials (New System Installation)", "total": 5500},
                {"description": "Labor (10.0 hours @ $95.0/hr)",                "total": 950},
                {"description": "Permit and inspection fees",                    "total": 250},
                {"description": "Refrigerant (5.0 lbs)",                        "total": 140},
                {"description": "Misc",                                          "total": 100},
                {"description": "Disposal Old Unit",                             "total": 150},
            ],
        },
    ],
}

# ── Generate ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out_dir = SCRIPT_DIR
    path = generate_contractor_pdf(
        SAMPLE_ESTIMATE,
        output_dir=out_dir,
        filename="estimate_preview.pdf",
    )
    print(f"✅  Generated: {path}")

    # Try to open it automatically
    import subprocess, platform
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception:
        print("   Open the file manually to review.")
