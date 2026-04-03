"""
ScopeSnap — SQLAlchemy ORM Models
ALL 12 tables from Tech Spec §02. Every column, every type, every constraint, every index.
DO NOT simplify — the schema is designed for future features.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Text, Boolean, Numeric, DateTime, ForeignKey,
    UniqueConstraint, Index, func, text
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY as PG_ARRAY, INT4RANGE
from db.types import SmartJSON, SmartUUID, SmartArray
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


# ── Helper ────────────────────────────────────────────────────────────────────
def new_uuid():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 1: companies
# Multi-tenant root. Every data record belongs to a company.
# ─────────────────────────────────────────────────────────────────────────────
class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # "abc-hvac" — used in report URLs

    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # e.g. "TACLA12345" — required on TX contractor docs

    address_line1: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    # Used for regional pricing lookups
    zip: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Stripe billing
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Tier management
    plan: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="free"
    )
    # 'free' | 'early_bird' | 'pro' | 'team'
    monthly_estimate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_estimate_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=5)
    # 5 (free), 50 (early_bird), NULL (pro/team = unlimited)

    settings: Mapped[dict] = mapped_column(SmartJSON, nullable=False, default=dict)
    # Default markup %, follow-up schedule, etc.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="company")
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="company")
    estimates: Mapped[List["Estimate"]] = relationship("Estimate", back_populates="company")
    properties: Mapped[List["Property"]] = relationship("Property", back_populates="company")
    pricing_rules: Mapped[List["PricingRule"]] = relationship("PricingRule", back_populates="company")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 2: users
# Technicians and owners. Clerk handles auth — we store Clerk user ID + role.
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    company_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    clerk_user_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # From Clerk JWT — never store passwords

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="tech")
    # 'owner' | 'tech' | 'admin'

    # Accuracy tracking (populated after 5+ completed estimates)
    accuracy_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    total_estimates: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="users")
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="user")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 3: properties
# Physical addresses. One property → many visits → property history feature.
# ─────────────────────────────────────────────────────────────────────────────
class Property(Base):
    __tablename__ = "properties"

    __table_args__ = (
        UniqueConstraint("company_id", "address_line1", "zip", name="uq_property_per_company"),
        # When tech types "4215 Oakwood Dr" + zip, we return existing property with history
        Index("idx_properties_company_address", "company_id", "address_line1", "zip"),
    )

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    company_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    # Properties are company-scoped (different companies may visit same address)

    address_line1: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    zip: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Customer info
    customer_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    customer_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Denormalized for quick display
    visit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_visit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="properties")
    equipment_instances: Mapped[List["EquipmentInstance"]] = relationship(
        "EquipmentInstance", back_populates="property"
    )
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="property")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 4: equipment_models  (GLOBAL — not company-scoped)
# Reference database. Known HVAC models with lifecycle data & failure patterns.
# THIS TABLE IS THE MOAT — seed with top 50, grows with every assessment.
# ─────────────────────────────────────────────────────────────────────────────
class EquipmentModel(Base):
    __tablename__ = "equipment_models"

    __table_args__ = (
        Index("idx_equipment_models_brand", "brand", "model_series"),
    )

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    # "Carrier"

    model_series: Mapped[str] = mapped_column(String(100), nullable=False)
    # "24ACC6" (the series, not the full model number)

    model_pattern: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # Regex: "24ACC6\d{2}[A-Z]\d{3}" — used for model matching

    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'ac_unit' | 'furnace' | 'heat_pump' | 'water_heater' | 'thermostat'

    seer_rating: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), nullable=True)
    tonnage_range: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # "2-5" (tons)

    manufacture_years: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # Stored as "2014-2022" for simplicity (PostgreSQL range type in future)

    avg_lifespan_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    known_issues: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # [{"component":"evap_coil","issue":"corrosion","onset_year":7,"frequency":"34%","regions":["gulf_coast"]}]

    recalls: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # [{"id":"CPSC-2023-xxx","component":"compressor","status":"active"}]

    serial_decode_pattern: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # {"year_chars":[0,1],"year_map":{"A":"2020","B":"2021"},"week_chars":[2,3]}

    replacement_models: Mapped[Optional[List[str]]] = mapped_column(SmartArray(Text), nullable=True)
    # Suggested replacement model numbers

    total_assessments: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Aggregate counter — how many times assessed across ALL companies (the moat metric)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    equipment_instances: Mapped[List["EquipmentInstance"]] = relationship(
        "EquipmentInstance", back_populates="equipment_model"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 5: equipment_instances
# A specific piece of equipment at a specific property.
# "Sarah's Carrier 24ACC636 installed in 2016."
# ─────────────────────────────────────────────────────────────────────────────
class EquipmentInstance(Base):
    __tablename__ = "equipment_instances"

    __table_args__ = (
        Index("idx_equipment_instances_property", "property_id"),
    )

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    property_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    equipment_model_id: Mapped[Optional[str]] = mapped_column(
        SmartUUID, ForeignKey("equipment_models.id", ondelete="SET NULL"), nullable=True
    )
    # NULL if AI couldn't match to known model

    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'ac_unit' | 'furnace' | 'heat_pump' | 'water_heater' | 'thermostat'

    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    install_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # From serial decode or tech estimate

    condition: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # 'excellent' | 'good' | 'fair' | 'poor' | 'critical'

    condition_details: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # {"coil":"moderate_corrosion","fins":"minor_bending","compressor":"normal"}

    photo_urls: Mapped[Optional[List[str]]] = mapped_column(SmartArray(Text), nullable=True)
    # Array of URLs for this specific equipment

    ai_confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    # 0-100. Vision API confidence in identification

    last_assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="equipment_instances")
    equipment_model: Mapped[Optional["EquipmentModel"]] = relationship(
        "EquipmentModel", back_populates="equipment_instances"
    )
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment", back_populates="equipment_instance"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 6: assessments
# A single site visit where a tech photographs equipment.
# One assessment → one estimate.
# ─────────────────────────────────────────────────────────────────────────────
class Assessment(Base):
    __tablename__ = "assessments"

    __table_args__ = (
        Index("idx_assessments_company", "company_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    company_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # The tech who performed the assessment

    property_id: Mapped[Optional[str]] = mapped_column(
        SmartUUID, ForeignKey("properties.id", ondelete="SET NULL"), nullable=True
    )
    equipment_instance_id: Mapped[Optional[str]] = mapped_column(
        SmartUUID, ForeignKey("equipment_instances.id", ondelete="SET NULL"), nullable=True
    )
    # Set after AI analysis links/creates equipment

    # Photos
    photo_urls: Mapped[List[str]] = mapped_column(SmartArray(Text), nullable=False)
    # 1-5 storage URLs
    voice_note_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # P1 feature — optional voice note URL

    # AI Analysis Results
    ai_analysis: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # Full Vision API response stored verbatim (for debugging and model improvement)

    ai_equipment_id: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # {"brand":"Carrier","model":"24ACC636A003","confidence":94.2,"serial":"...","install_year":2016}

    ai_condition: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # {"overall":"fair","components":[{"name":"evap_coil","condition":"moderate_corrosion","severity":"high"}]}

    ai_issues: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # [{"component":"evap_coil","issue":"corrosion","severity":"high","description":"Green oxide..."}]

    tech_overrides: Mapped[dict] = mapped_column(SmartJSON, nullable=False, default=dict)
    # Any fields the tech manually corrected. Used to train better prompts.

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    # 'pending' | 'analyzed' | 'estimated' | 'sent' | 'approved' | 'completed'

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="assessments")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="assessments")
    property: Mapped[Optional["Property"]] = relationship("Property", back_populates="assessments")
    equipment_instance: Mapped[Optional["EquipmentInstance"]] = relationship(
        "EquipmentInstance", back_populates="assessments"
    )
    estimate: Mapped[Optional["Estimate"]] = relationship(
        "Estimate", back_populates="assessment", uselist=False
    )
    photos: Mapped[List["AssessmentPhoto"]] = relationship(
        "AssessmentPhoto", back_populates="assessment"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 7: assessment_photos
# Individual photos within an assessment with their AI annotations.
# Needed for annotated photo feature in homeowner report.
# ─────────────────────────────────────────────────────────────────────────────
class AssessmentPhoto(Base):
    __tablename__ = "assessment_photos"

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    assessment_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False
    )

    photo_url: Mapped[str] = mapped_column(Text, nullable=False)
    # URL — original photo

    annotated_photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # URL — photo with AI annotations overlaid

    annotations: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # [{"type":"circle","x":125,"y":85,"r":30,"color":"red","label":"CORROSION","description":"Green oxide..."}]

    ai_raw_response: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # Full vision API response for this specific photo

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="photos")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 8: estimates
# The pricing output from an assessment. Good/Better/Best options + status.
# ─────────────────────────────────────────────────────────────────────────────
class Estimate(Base):
    __tablename__ = "estimates"

    __table_args__ = (
        Index("idx_estimates_company", "company_id", "status", "created_at"),
        Index("idx_estimates_report_token", "report_token"),
    )

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    assessment_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    # 1:1 relationship with assessment

    company_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    # Denormalized for faster queries

    report_token: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    # Random token for public report URL. NOT the UUID — never expose internal IDs.

    report_short_id: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    # Human-readable: "rpt-0847". For display in SMS/email.

    # The Good/Better/Best options
    options: Mapped[dict] = mapped_column(SmartJSON, nullable=False)
    # [{"tier":"good","name":"Clean & Treat","total":450.00,"line_items":[...]}, ...]

    selected_option: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # 'good' | 'better' | 'best' — set when customer approves

    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    # Of selected option
    deposit_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    # Usually 20% of total

    markup_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=35.0)
    # Company default, tech can override per estimate

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    # 'draft' | 'sent' | 'viewed' | 'approved' | 'deposit_paid' | 'completed' | 'expired'

    # Timestamps for status tracking
    viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Set when homeowner first opens report link
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Stripe
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Document URLs
    contractor_pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Storage URL for contractor-facing PDF
    homeowner_report_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Public URL: report.scopesnap.com/{slug}/rpt-{short_id}

    # Delivery tracking
    sent_via: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # 'email' | 'sms' | 'both'
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Accuracy tracking (filled in after job completion)
    actual_cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    accuracy_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    # Calculated: 100 - abs(estimate - actual) / actual * 100

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="estimate")
    company: Mapped["Company"] = relationship("Company", back_populates="estimates")
    line_items: Mapped[List["EstimateLineItem"]] = relationship(
        "EstimateLineItem", back_populates="estimate", cascade="all, delete-orphan"
    )
    documents: Mapped[List["EstimateDocument"]] = relationship(
        "EstimateDocument", back_populates="estimate", cascade="all, delete-orphan"
    )
    follow_ups: Mapped[List["FollowUp"]] = relationship(
        "FollowUp", back_populates="estimate", cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 9: estimate_line_items
# Individual line items within each estimate option.
# ─────────────────────────────────────────────────────────────────────────────
class EstimateLineItem(Base):
    __tablename__ = "estimate_line_items"

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    estimate_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("estimates.id", ondelete="CASCADE"), nullable=False
    )

    option_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    # 'good' | 'better' | 'best'

    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'parts' | 'labor' | 'permits' | 'disposal' | 'refrigerant'

    description: Mapped[str] = mapped_column(String(300), nullable=False)
    # e.g. "Carrier evaporator coil — 24ACC636 compatible"

    quantity: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=1)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # From pricing DB or tech override
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # quantity × unit_cost — stored (not calculated) to avoid floating point drift

    source: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pricing_db")
    # 'ai' | 'pricing_db' | 'tech_override' — track where each line came from

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    estimate: Mapped["Estimate"] = relationship("Estimate", back_populates="line_items")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 10: estimate_documents
# Generated documents (PDFs, reports) attached to an estimate.
# ─────────────────────────────────────────────────────────────────────────────
class EstimateDocument(Base):
    __tablename__ = "estimate_documents"

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    estimate_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("estimates.id", ondelete="CASCADE"), nullable=False
    )

    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'contractor_pdf' | 'homeowner_report' | 'invoice'

    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    # Storage URL

    file_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    estimate: Mapped["Estimate"] = relationship("Estimate", back_populates="documents")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 11: pricing_rules
# Company-specific or regional pricing overrides.
# Cascade: company → region → national default.
# ─────────────────────────────────────────────────────────────────────────────
class PricingRule(Base):
    __tablename__ = "pricing_rules"

    __table_args__ = (
        UniqueConstraint("company_id", "equipment_type", "job_type", "region", name="uq_pricing_rule"),
        Index("idx_pricing_rules_lookup", "company_id", "equipment_type", "job_type", "region"),
    )

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    company_id: Mapped[Optional[str]] = mapped_column(
        SmartUUID, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    # NULL = global default. Non-null = company-specific override.

    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'ac_unit' | 'furnace' | 'heat_pump' | etc.

    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'coil_replacement' | 'full_system' | 'compressor_replacement' |
    # 'refrigerant_recharge' | 'maintenance' | 'repair'

    region: Mapped[str] = mapped_column(String(20), nullable=False, server_default="national")
    # 'houston_metro' | 'national' | state code

    parts_cost: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # {"min":1200,"max":2200,"avg":1850,"source":"manufacturer_list"}

    labor_hours: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # {"min":3,"max":6,"avg":4.5}

    labor_rate: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    # $/hour — company sets this

    permit_cost: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    # Regional average

    refrigerant_cost_per_lb: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    # Current market rate — needs periodic update

    additional_costs: Mapped[Optional[dict]] = mapped_column(SmartJSON, nullable=True)
    # {"disposal_fee":75,"crane_if_rooftop":500}

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="pricing_rules")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 12: follow_ups
# Scheduled follow-up messages. Cancelled if estimate is approved first.
# ─────────────────────────────────────────────────────────────────────────────
class FollowUp(Base):
    __tablename__ = "follow_ups"

    __table_args__ = (
        Index(
            "idx_follow_ups_scheduled", "scheduled_at",
            postgresql_where=text("sent_at IS NULL AND cancelled = false")
        ),
    )

    id: Mapped[str] = mapped_column(
        SmartUUID, primary_key=True, default=new_uuid
    )
    estimate_id: Mapped[str] = mapped_column(
        SmartUUID, ForeignKey("estimates.id", ondelete="CASCADE"), nullable=False
    )

    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 'email' | 'sms'

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # NULL until actually sent

    cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Cancelled if estimate is approved before follow-up fires

    template: Mapped[str] = mapped_column(String(50), nullable=False)
    # '24h_reminder' | '48h_reminder' | '7d_last_chance'

    # Relationships
    estimate: Mapped["Estimate"] = relationship("Estimate", back_populates="follow_ups")


# ─────────────────────────────────────────────────────────────────────────────
# All models list — used by Alembic env.py
# ─────────────────────────────────────────────────────────────────────────────
__all__ = [
    "Base",
    "Company",
    "User",
    "Property",
    "EquipmentModel",
    "EquipmentInstance",
    "Assessment",
    "AssessmentPhoto",
    "Estimate",
    "EstimateLineItem",
    "EstimateDocument",
    "PricingRule",
    "FollowUp",
]
