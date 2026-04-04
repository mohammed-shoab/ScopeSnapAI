"""
SnapAI — Analytics API Endpoints
WP-14: Owner Dashboard analytics.

Provides company-level performance metrics for the owner dashboard:
- Revenue overview (total, this month, avg per estimate)
- Estimate funnel (draft → sent → viewed → approved → paid)
- AI accuracy score (predicted vs actual cost)
- Tech performance (estimates per tech, approval rates)
- Recent activity feed
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from db.database import get_db
from db.models import Assessment, Company, Estimate, User, Property
from api.auth import get_current_user, AuthContext, require_admin

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# ── GET /api/analytics/dashboard ─────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard_analytics(
    days: int = 30,   # Lookback window
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-14: Returns comprehensive analytics for the owner dashboard.

    Query params:
    - days: lookback window (default: 30 days)

    Returns:
    - revenue: total, this_period, avg_per_estimate, pending_deposits
    - funnel: counts at each stage (draft→sent→viewed→approved→paid)
    - conversion_rate: approved/sent %
    - ai_accuracy: avg accuracy score across completed estimates
    - recent_estimates: last 10 for the activity feed
    - period_label: human-readable period description
    """
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)
    company_id = auth.company_id

    # ── Load all estimates for this company ───────────────────────────────────
    all_result = await db.execute(
        select(Estimate).where(Estimate.company_id == company_id)
    )
    all_estimates = all_result.scalars().all()

    # ── Period estimates ──────────────────────────────────────────────────────
    period_estimates = [e for e in all_estimates if e.created_at and e.created_at >= period_start]

    # ── Revenue metrics ───────────────────────────────────────────────────────
    approved_all = [e for e in all_estimates if e.status in ("approved", "deposit_paid", "completed")]
    approved_period = [e for e in period_estimates if e.status in ("approved", "deposit_paid", "completed")]
    paid_deposits = [e for e in all_estimates if e.status == "deposit_paid"]

    total_revenue = sum(float(e.total_amount or 0) for e in approved_all)
    period_revenue = sum(float(e.total_amount or 0) for e in approved_period)
    pending_deposits = sum(
        float(e.deposit_amount or 0)
        for e in all_estimates
        if e.status == "approved" and e.deposit_amount
    )
    avg_per_estimate = (
        period_revenue / len(approved_period) if approved_period else 0
    )

    # ── Funnel counts ─────────────────────────────────────────────────────────
    def count_status(estimates, statuses):
        if isinstance(statuses, str):
            statuses = [statuses]
        return sum(1 for e in estimates if e.status in statuses)

    funnel = {
        "draft":         count_status(all_estimates, "draft"),
        "estimated":     count_status(all_estimates, "estimated"),
        "sent":          count_status(all_estimates, ["sent", "viewed"]),
        "viewed":        count_status(all_estimates, ["viewed"]) + count_status(all_estimates, ["approved", "deposit_paid", "completed"]),
        "approved":      count_status(all_estimates, ["approved", "deposit_paid", "completed"]),
        "deposit_paid":  count_status(all_estimates, "deposit_paid"),
        "total":         len(all_estimates),
    }

    # ── Conversion rates ──────────────────────────────────────────────────────
    sent_count = count_status(all_estimates, ["sent", "viewed", "approved", "deposit_paid", "completed"])
    approved_count = count_status(all_estimates, ["approved", "deposit_paid", "completed"])
    conversion_rate = round(approved_count / sent_count * 100, 1) if sent_count > 0 else 0
    view_rate = round(funnel["viewed"] / sent_count * 100, 1) if sent_count > 0 else 0

    # ── AI Accuracy ───────────────────────────────────────────────────────────
    scored = [e for e in all_estimates if e.accuracy_score is not None]
    avg_accuracy = round(
        sum(float(e.accuracy_score) for e in scored) / len(scored), 1
    ) if scored else None

    # ── Recent estimates (last 10) ────────────────────────────────────────────
    recent = sorted(all_estimates, key=lambda e: e.created_at or datetime.min, reverse=True)[:10]
    recent_data = []
    for e in recent:
        recent_data.append({
            "id": str(e.id),
            "report_short_id": e.report_short_id,
            "status": e.status,
            "total_amount": float(e.total_amount) if e.total_amount else None,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "approved_at": e.approved_at.isoformat() if e.approved_at else None,
            "viewed_at": e.viewed_at.isoformat() if e.viewed_at else None,
        })

    # ── Monthly trend (last 6 months) ─────────────────────────────────────────
    # Use proper calendar month arithmetic to avoid duplicate month names
    # (using timedelta(days=30) can land on the same month for consecutive entries)
    monthly_trend = []
    for i in range(5, -1, -1):
        # Compute month offset by adjusting year/month directly
        target_month = now.month - i
        target_year = now.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        month_start = datetime(target_year, target_month, 1, 0, 0, 0, tzinfo=timezone.utc)

        # Month end = first day of next month
        if target_month == 12:
            month_end = datetime(target_year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        else:
            month_end = datetime(target_year, target_month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        # For the current month, don't go beyond now
        if i == 0:
            month_end = now

        month_ests = [
            e for e in all_estimates
            if e.created_at and month_start <= e.created_at < month_end
        ]
        month_approved = [
            e for e in month_ests
            if e.status in ("approved", "deposit_paid", "completed")
        ]
        monthly_trend.append({
            "month": month_start.strftime("%b %Y"),
            "estimates": len(month_ests),
            "approved": len(month_approved),
            "revenue": round(sum(float(e.total_amount or 0) for e in month_approved), 2),
        })

    # ── Property stats ────────────────────────────────────────────────────────
    prop_result = await db.execute(
        select(Property).where(Property.company_id == company_id)
    )
    properties = prop_result.scalars().all()
    repeat_customers = sum(1 for p in properties if (p.visit_count or 0) >= 2)

    return {
        "period_days": days,
        "period_label": f"Last {days} days",
        "generated_at": now.isoformat(),

        "revenue": {
            "total_all_time": round(total_revenue, 2),
            "this_period": round(period_revenue, 2),
            "avg_per_estimate": round(avg_per_estimate, 2),
            "pending_deposits": round(pending_deposits, 2),
        },

        "funnel": funnel,
        "conversion_rate": conversion_rate,
        "view_rate": view_rate,

        "ai_accuracy": avg_accuracy,

        "properties": {
            "total": len(properties),
            "repeat_customers": repeat_customers,
        },

        "monthly_trend": monthly_trend,
        "recent_estimates": recent_data,
    }


# ── GET /api/analytics/estimates-summary ─────────────────────────────────────

@router.get("/estimates-summary")
async def get_estimates_summary(
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lightweight summary for the tech dashboard (all roles can access)."""
    company_id = auth.company_id

    result = await db.execute(
        select(Estimate).where(Estimate.company_id == company_id)
    )
    estimates = result.scalars().all()

    total = len(estimates)
    sent = sum(1 for e in estimates if e.status in ("sent", "viewed", "approved", "deposit_paid", "completed"))
    approved = sum(1 for e in estimates if e.status in ("approved", "deposit_paid", "completed"))
    revenue = sum(float(e.total_amount or 0) for e in estimates if e.status in ("approved", "deposit_paid", "completed"))

    return {
        "total": total,
        "sent": sent,
        "approved": approved,
        "revenue": round(revenue, 2),
        "conversion_rate": round(approved / sent * 100, 1) if sent > 0 else 0,
    }


# ── GET /api/analytics/tech-performance ──────────────────────────────────────

@router.get("/tech-performance")
async def get_tech_performance(
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-14: Per-technician accuracy and approval rates.
    Returns accuracy scores, estimate counts, and approval rates per tech.
    """
    company_id = auth.company_id

    users_result = await db.execute(
        select(User).where(User.company_id == company_id)
    )
    techs = users_result.scalars().all()

    est_result = await db.execute(
        select(Estimate).where(Estimate.company_id == company_id)
    )
    all_estimates = est_result.scalars().all()

    # Build assessment → user mapping
    assess_result = await db.execute(
        select(Assessment).where(Assessment.company_id == company_id)
    )
    assessments = {a.id: a for a in assess_result.scalars().all()}

    tech_data = []
    for tech in techs:
        tech_estimates = [
            e for e in all_estimates
            if e.assessment_id in assessments
            and assessments[e.assessment_id].user_id == tech.id
        ]
        total = len(tech_estimates)
        approved = sum(1 for e in tech_estimates if e.status in ("approved", "deposit_paid", "completed"))
        scored = [e for e in tech_estimates if e.accuracy_score is not None]
        avg_accuracy = round(
            sum(float(e.accuracy_score) for e in scored) / len(scored), 1
        ) if scored else float(tech.accuracy_score) if tech.accuracy_score else None

        tech_data.append({
            "id": str(tech.id),
            "name": tech.name,
            "role": tech.role,
            "total_estimates": total,
            "approved_estimates": approved,
            "approval_rate": round(approved / total * 100, 1) if total > 0 else 0,
            "accuracy_score": avg_accuracy,
        })

    return {"technicians": tech_data}


# ── GET /api/analytics/benchmarks ────────────────────────────────────────────

@router.get("/benchmarks")
async def get_benchmarks(
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-14: Industry benchmark comparison (placeholder with mock data).
    In production, this would pull from a shared benchmark dataset.
    """
    company_id = auth.company_id

    est_result = await db.execute(
        select(Estimate).where(Estimate.company_id == company_id)
    )
    estimates = est_result.scalars().all()

    approved = [e for e in estimates if e.status in ("approved", "deposit_paid", "completed")]
    avg_job = round(
        sum(float(e.total_amount or 0) for e in approved) / len(approved), 2
    ) if approved else 0

    return {
        "region": "Your Area",
        "your_metrics": {
            "avg_job_value": avg_job,
            "conversion_rate": round(
                len(approved) / max(len(estimates), 1) * 100, 1
            ),
            "total_estimates": len(estimates),
        },
        "industry_avg": {
            "avg_job_value": 4200.00,
            "conversion_rate": 34.0,
            "avg_response_time_hrs": 2.4,
        },
        "percentile": {
            "job_value": 65,
            "conversion": 72,
            "response_time": 80,
        },
    }


# ── GET /api/analytics/profit-leaks ──────────────────────────────────────────

@router.get("/profit-leaks")
async def get_profit_leaks(
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-14: Identifies potential profit leaks (placeholder with mock data).
    In production, this would analyze estimate vs actual cost data.
    """
    return {
        "leaks": [
            {
                "category": "Compressor Replacements",
                "avg_underestimate": 340,
                "occurrences": 12,
                "total_impact": 4080,
                "severity": "high",
            },
            {
                "category": "Duct Modifications",
                "avg_underestimate": 180,
                "occurrences": 8,
                "total_impact": 1440,
                "severity": "medium",
            },
            {
                "category": "Refrigerant Recharge",
                "avg_underestimate": 95,
                "occurrences": 15,
                "total_impact": 1425,
                "severity": "medium",
            },
        ],
        "total_annual_impact": 6945,
    }


# ── GET /api/analytics/aging-alerts ──────────────────────────────────────────

@router.get("/aging-alerts")
async def get_aging_alerts(
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-14: Equipment aging alerts (placeholder with mock data).
    In production, this would analyze equipment install dates and lifespans.
    """
    return {
        "alerts": [
            {
                "equipment_type": "Carrier 24ACC6",
                "count": 23,
                "avg_age_years": 14,
                "expected_lifespan": 15,
                "risk_level": "high",
            },
            {
                "equipment_type": "Trane XR15",
                "count": 18,
                "avg_age_years": 12,
                "expected_lifespan": 15,
                "risk_level": "medium",
            },
            {
                "equipment_type": "Lennox XC21",
                "count": 11,
                "avg_age_years": 10,
                "expected_lifespan": 18,
                "risk_level": "low",
            },
        ],
        "total_at_risk": 52,
    }
