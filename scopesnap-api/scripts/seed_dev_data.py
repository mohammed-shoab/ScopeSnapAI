"""
SnapAI — Dev Data Seeder
Populates the database with realistic estimates, properties, and assessments
for test_user_mike so the dashboard KPIs and analytics show meaningful data.

Usage (from project root):
    docker compose exec api python scripts/seed_dev_data.py

Idempotent: skips records that already exist, safe to run multiple times.
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
from random import choice, randint, uniform

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from db.database import AsyncSessionLocal
from db.models import Company, User, Property, Assessment, Estimate

# ── Config ────────────────────────────────────────────────────────────────────

DEV_CLERK_USER_ID = "test_user_mike"

# Realistic HVAC scenarios
PROPERTIES = [
    {"customer_name": "James & Linda Okafor", "customer_email": "jokafor@gmail.com",
     "customer_phone": "602-555-0112", "address_line1": "4821 E Desert Flower Ln",
     "city": "Phoenix", "state": "AZ", "zip": "85044"},
    {"customer_name": "Marcus Delgado", "customer_email": "mdelgado@outlook.com",
     "customer_phone": "480-555-0293", "address_line1": "1147 W Mesquite Dr",
     "city": "Chandler", "state": "AZ", "zip": "85224"},
    {"customer_name": "Sarah & Tom Patel", "customer_email": "spatelproperty@gmail.com",
     "customer_phone": "623-555-0441", "address_line1": "9034 N 67th Ave",
     "city": "Glendale", "state": "AZ", "zip": "85302"},
    {"customer_name": "Robert Chen", "customer_email": "rchen.home@yahoo.com",
     "customer_phone": "480-555-0178", "address_line1": "2255 S Dobson Rd #1104",
     "city": "Mesa", "state": "AZ", "zip": "85202"},
    {"customer_name": "Angela Morrison", "customer_email": "a.morrison@homemail.com",
     "customer_phone": "602-555-0355", "address_line1": "7712 E Camelback Rd",
     "city": "Scottsdale", "state": "AZ", "zip": "85251"},
    {"customer_name": "David & Maria Gutierrez", "customer_email": "gutierrez.family@gmail.com",
     "customer_phone": "480-555-0627", "address_line1": "3318 W Thunderbird Rd",
     "city": "Phoenix", "state": "AZ", "zip": "85053"},
    {"customer_name": "Kevin Tran", "customer_email": "ktran.hvac@gmail.com",
     "customer_phone": "602-555-0819", "address_line1": "500 N Miller Rd #204",
     "city": "Scottsdale", "state": "AZ", "zip": "85257"},
    {"customer_name": "Patricia Williams", "customer_email": "pwilliams99@aol.com",
     "customer_phone": "623-555-0934", "address_line1": "15224 W Waddell Rd",
     "city": "Surprise", "state": "AZ", "zip": "85379"},
]

# Estimate options templates: (subtotal, markup_pct, tier_name, status, days_ago)
ESTIMATE_SCENARIOS = [
    # Recently approved + deposit paid (high-value)
    {"status": "deposit_paid", "days_ago": 3,  "total": 8450.00,  "tier": "better",
     "approved_offset": 2, "viewed_offset": 1, "sent_offset": 1},
    # Approved, no deposit yet
    {"status": "approved",     "days_ago": 5,  "total": 5200.00,  "tier": "better",
     "approved_offset": 1, "viewed_offset": 1, "sent_offset": 2},
    # Viewed, not yet approved
    {"status": "viewed",       "days_ago": 7,  "total": 3800.00,  "tier": "good",
     "approved_offset": None, "viewed_offset": 2, "sent_offset": 4},
    # Sent last week
    {"status": "sent",         "days_ago": 10, "total": 6100.00,  "tier": "best",
     "approved_offset": None, "viewed_offset": None, "sent_offset": 6},
    # Another deposit paid (older, high revenue)
    {"status": "deposit_paid", "days_ago": 14, "total": 9200.00,  "tier": "best",
     "approved_offset": 8, "viewed_offset": 5, "sent_offset": 10},
    # Approved last month
    {"status": "approved",     "days_ago": 20, "total": 4400.00,  "tier": "better",
     "approved_offset": 12, "viewed_offset": 10, "sent_offset": 16},
    # Sent, cold lead
    {"status": "sent",         "days_ago": 22, "total": 7800.00,  "tier": "best",
     "approved_offset": None, "viewed_offset": None, "sent_offset": 18},
    # Estimated (not sent yet)
    {"status": "estimated",    "days_ago": 1,  "total": 2950.00,  "tier": "good",
     "approved_offset": None, "viewed_offset": None, "sent_offset": None},
]

def _make_options(total: float, tier: str) -> list:
    """Generate realistic Good/Better/Best options based on selected total."""
    subtotal = round(total / 1.35, 2)
    good_sub  = round(subtotal * 0.72, 2)
    best_sub  = round(subtotal * 1.20, 2)

    def _mk(t, name, sub, desc, seer_new, savings_annual):
        tot = round(sub * 1.35, 2)
        return {
            "tier": t,
            "name": name,
            "description": desc,
            "subtotal": sub,
            "total": tot,
            "markup_percent": 35.0,
            "total_after_rebate": tot,
            "five_year_total": round(tot + savings_annual * 5 * 0.12, 2),
            "rebate_available": 0,
            "energy_savings": {
                "annual_savings": savings_annual,
                "five_year_savings": savings_annual * 5,
                "seer_improvement_pct": round((seer_new - 10) / 10 * 100, 1),
                "current_seer": 10.0,
                "new_seer": seer_new,
            },
            "line_items": [
                {"category": "parts",  "description": "New condenser unit",      "quantity": 1, "total": round(sub * 0.45)},
                {"category": "parts",  "description": "Air handler / coil",      "quantity": 1, "total": round(sub * 0.25)},
                {"category": "labor",  "description": "Installation labor",       "quantity": 1, "total": round(sub * 0.22)},
                {"category": "fees",   "description": "Permit & disposal",        "quantity": 1, "total": round(sub * 0.08)},
            ],
        }

    return [
        _mk("good",   "Standard Efficiency (14 SEER)",   good_sub,
            "Basic replacement. Meets code minimum. Best upfront value.",
            14, 280),
        _mk("better", "High Efficiency (18 SEER)",        subtotal,
            "Recommended. Rebate-eligible. Significant energy savings.",
            18, 420),
        _mk("best",   "Premium Comfort (21 SEER + smart)", best_sub,
            "Variable-speed compressor, smart thermostat, lowest energy bills.",
            21, 580),
    ]


async def seed():
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        # ── Find test user ────────────────────────────────────────────────────
        user_result = await db.execute(
            select(User).where(User.clerk_user_id == DEV_CLERK_USER_ID)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            print(f"❌ User '{DEV_CLERK_USER_ID}' not found in DB.")
            print("   Run: POST /api/webhooks/clerk with the user provisioning payload first.")
            return

        company_id = user.company_id
        user_id = user.id

        company_result = await db.execute(select(Company).where(Company.id == company_id))
        company = company_result.scalar_one_or_none()
        print(f"✓ Found user: {user.email} / company: {company.name if company else '?'}")

        # ── Check existing data ───────────────────────────────────────────────
        existing_props = await db.execute(
            select(Property).where(Property.company_id == company_id)
        )
        existing_count = len(existing_props.scalars().all())
        if existing_count >= 5:
            print(f"ℹ  {existing_count} properties already exist — skipping seed.")
            print("   To re-seed, delete existing properties first.")
            return

        print(f"\n📦 Seeding {len(PROPERTIES)} properties + {len(ESTIMATE_SCENARIOS)} estimates...\n")

        created_estimates = []

        for i, prop_data in enumerate(PROPERTIES):
            # Create property
            prop = Property(
                company_id=company_id,
                customer_name=prop_data["customer_name"],
                customer_email=prop_data["customer_email"],
                customer_phone=prop_data["customer_phone"],
                address_line1=prop_data["address_line1"],
                city=prop_data["city"],
                state=prop_data["state"],
                zip=prop_data["zip"],
                property_type="residential",
                square_footage=choice([1200, 1500, 1800, 2100, 2400, 2800]),
                year_built=choice([1985, 1990, 1995, 2000, 2005, 2008, 2012]),
            )
            db.add(prop)
            await db.flush()

            # Only create estimates for scenarios (may be fewer than properties)
            if i >= len(ESTIMATE_SCENARIOS):
                print(f"  Property {i+1}: {prop_data['customer_name']} — (no estimate)")
                continue

            scenario = ESTIMATE_SCENARIOS[i]
            days_ago = scenario["days_ago"]
            created_at = now - timedelta(days=days_ago)

            # Create assessment (simplified — no AI analysis needed for seed data)
            assessment = Assessment(
                company_id=company_id,
                property_id=prop.id,
                user_id=user_id,
                status="estimated" if scenario["status"] != "estimated" else "estimated",
                created_at=created_at,
                ai_analysis={
                    "equipment_type": "ac_unit",
                    "overall_condition": choice(["fair", "poor", "critical"]),
                    "estimated_age_years": randint(10, 20),
                    "confidence_score": round(uniform(0.78, 0.95), 2),
                    "recommended_action": "full_system",
                    "issues": [
                        {"component": "compressor", "severity": "high",
                         "issue": "Excessive cycling due to age and wear",
                         "description_plain": "Unit is nearing end of service life"},
                    ],
                },
                ai_issues=[
                    {"component": "Compressor", "severity": "high",
                     "issue": "Excessive cycling", "description_plain": "End of service life"},
                ],
            )
            db.add(assessment)
            await db.flush()

            # Create estimate with proper timestamps
            total = scenario["total"]
            tier = scenario["tier"]
            est_status = scenario["status"]
            options = _make_options(total, tier)

            # Build short ID
            import secrets, string
            digits = "".join(secrets.choice(string.digits) for _ in range(4))
            short_id = f"rpt-{digits}"

            # Timestamps
            sent_at = (created_at + timedelta(hours=2)) if scenario["sent_offset"] else None
            viewed_at = None
            if scenario.get("viewed_offset"):
                viewed_at = created_at + timedelta(hours=scenario["viewed_offset"] * 8)
            approved_at = None
            if scenario.get("approved_offset"):
                approved_at = created_at + timedelta(hours=scenario["approved_offset"] * 8)

            estimate = Estimate(
                assessment_id=assessment.id,
                company_id=company_id,
                report_token=secrets.token_urlsafe(32)[:32],
                report_short_id=short_id,
                options=options,
                selected_option=tier,
                markup_percent=35.0,
                total_amount=Decimal(str(total)),
                deposit_amount=Decimal(str(round(total * 0.20, 2))),
                status=est_status,
                created_at=created_at,
                sent_at=sent_at,
                sent_via="email" if sent_at else None,
                viewed_at=viewed_at,
                approved_at=approved_at,
                homeowner_report_url=f"/r/{company.slug if company else 'hvac'}/{short_id}",
            )
            db.add(estimate)
            await db.flush()
            created_estimates.append(estimate)

            status_icon = {"deposit_paid": "💰", "approved": "✅", "viewed": "👁",
                           "sent": "📤", "estimated": "📋"}.get(est_status, "📋")
            print(f"  {status_icon} {prop_data['customer_name'][:25]:<25} "
                  f"  {short_id}  ${total:,.0f}  [{est_status}]")

        await db.commit()

        # ── Also add some older estimates (30-90 days) for trend data ────────
        print("\n📈 Adding historical trend data (30-90 days)...")
        historical = [
            {"days_ago": 35, "total": 5800, "status": "approved"},
            {"days_ago": 42, "total": 3200, "status": "sent"},
            {"days_ago": 48, "total": 7100, "status": "deposit_paid"},
            {"days_ago": 55, "total": 4500, "status": "approved"},
            {"days_ago": 63, "total": 8800, "status": "deposit_paid"},
            {"days_ago": 71, "total": 2900, "status": "estimated"},
            {"days_ago": 79, "total": 6300, "status": "approved"},
            {"days_ago": 88, "total": 5100, "status": "deposit_paid"},
        ]

        for h in historical:
            # Create minimal property + assessment + estimate
            hist_prop = Property(
                company_id=company_id,
                customer_name=f"Historical Customer {h['days_ago']}d",
                customer_email=f"hist{h['days_ago']}@example.com",
                address_line1=f"{randint(1000,9999)} N Historical Blvd",
                city="Phoenix", state="AZ",
                zip="85001",
                property_type="residential",
            )
            db.add(hist_prop)
            await db.flush()

            hist_assessment = Assessment(
                company_id=company_id,
                property_id=hist_prop.id,
                user_id=user_id,
                status="estimated",
                created_at=now - timedelta(days=h["days_ago"]),
            )
            db.add(hist_assessment)
            await db.flush()

            digits = "".join(secrets.choice(string.digits) for _ in range(4))
            hist_short_id = f"rpt-{digits}"
            hist_created = now - timedelta(days=h["days_ago"])
            hist_est = Estimate(
                assessment_id=hist_assessment.id,
                company_id=company_id,
                report_token=secrets.token_urlsafe(32)[:32],
                report_short_id=hist_short_id,
                options=_make_options(h["total"], "better"),
                selected_option="better",
                markup_percent=35.0,
                total_amount=Decimal(str(h["total"])),
                deposit_amount=Decimal(str(round(h["total"] * 0.20, 2))),
                status=h["status"],
                created_at=hist_created,
                sent_at=hist_created + timedelta(hours=3) if h["status"] != "estimated" else None,
                sent_via="email" if h["status"] != "estimated" else None,
                approved_at=hist_created + timedelta(days=2) if h["status"] in ("approved", "deposit_paid") else None,
                homeowner_report_url=f"/r/{company.slug if company else 'hvac'}/{hist_short_id}",
            )
            db.add(hist_est)

        await db.commit()
        print("  ✓ Historical data committed\n")

        # ── Summary ───────────────────────────────────────────────────────────
        total_est = await db.execute(
            select(Estimate).where(Estimate.company_id == company_id)
        )
        all_est = total_est.scalars().all()
        total_revenue = sum(
            float(e.total_amount or 0)
            for e in all_est
            if e.status in ("approved", "deposit_paid", "completed")
        )
        print("=" * 60)
        print(f"✅ SEED COMPLETE")
        print(f"   Properties:  {len(PROPERTIES) + len(historical)}")
        print(f"   Estimates:   {len(all_est)}")
        print(f"   Revenue:     ${total_revenue:,.0f} (approved/paid)")
        print("=" * 60)
        print("\n🌐 Reload the dashboard at http://localhost:3000/dashboard")
        print("   Analytics at http://localhost:3000/analytics\n")


if __name__ == "__main__":
    asyncio.run(seed())
