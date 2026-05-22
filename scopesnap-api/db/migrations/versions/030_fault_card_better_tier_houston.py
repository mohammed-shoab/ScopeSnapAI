# coding: utf-8
"""Add Better-tier description + why_recommended to all 19 Houston fault_cards.

Revision ID: 030
Revises: 029
Create Date: 2026-05-22

Fills the only gap in Houston fault_cards.better_option_estimate:
- Migrations 021 added Good, Best-comprehensive, Best-replacement copy.
- This migration adds the middle (Better / Tier-B) description + why_recommended
  for all 19 cards.  The "Why recommended?" collapsible in ReportClient.tsx
  requires why_recommended to be non-null to render.

Copy source: SnapAI Houston Better-Tier Copy v1 (2026-05-22)
Character limit: 180 per field (verified).
Market: US / Houston.  No Pakistan-specific language.
"""
import json
from alembic import op

revision = "030"
down_revision = "029"
branch_labels = None
depends_on = None

_CARDS = {
    1: {
        "description": "Replace capacitor and contactor as a pair. Verify terminal torques. Prevents the next electrical failure on a unit already showing age-related stress.",
        "why_recommended": "Capacitor failure stresses the contactor on every start cycle. A pitted contactor left in place fails within months, adding another service call and visit fee.",
    },
    2: {
        "description": "Replace filter and clean the evaporator coil. A dirty coil behind a neglected filter loses 15-25% capacity and won't recover on filter change alone.",
        "why_recommended": "A dirty filter running for weeks means the coil is fouled too. Skipping coil cleaning leaves capacity loss and risks a freeze-up call within days in Houston heat.",
    },
    3: {
        "description": "Replace the contactor and capacitor together. Both wear on the same cycle — replacing one without the other invites the second failure within 90 days.",
        "why_recommended": "Contactor and capacitor degrade on the same electrical stress cycle. Replacing only the contactor leaves a weakened cap that fails next hot afternoon, same trip fee.",
    },
    4: {
        "description": "Replace blower motor and run capacitor together. A weak capacitor hard-starts the new motor, cutting its life in Houston's near-continuous AC season.",
        "why_recommended": "New motors fail early when paired with a degraded capacitor. One return call for motor burnout costs more than replacing both parts today on the same visit.",
    },
    5: {
        "description": "Clear the drain, add an algaecide tablet, and install a float safety switch. The switch shuts the unit off before attic water damage if the line clogs again.",
        "why_recommended": "Houston humidity refills a cleared drain with algae in 60-90 days. Without the float switch, the next clog overflows the pan and causes ceiling water damage.",
    },
    6: {
        "description": "Repair the fault and apply anti-corrosion compound to all adjacent terminals. Stops the current failure and slows corrosion on connections most at risk.",
        "why_recommended": "Heat damage at one terminal means adjacent connections are already stressed. Leaving them untreated puts 60-70% odds on a second wiring fault within 12 months.",
    },
    7: {
        "description": "Replace the control board and upgrade to a smart thermostat. Eliminates the error code and prevents compatibility faults that cause premature board failures.",
        "why_recommended": "Old thermostats send voltage spikes that shorten replacement board life to 2-3 years. Upgrading both in one visit costs less than a second board swap next season.",
    },
    8: {
        "description": "Seal the leak, install a new filter dryer, and recharge to manufacturer spec. The dryer removes moisture that entered the refrigerant circuit during the leak.",
        "why_recommended": "Moisture enters the circuit during any leak event. Skipping the dryer leaves it there, corroding the TXV and causing another refrigerant leak within 12-18 months.",
    },
    9: {
        "description": "Thaw and chemically clean the evaporator coil, replace the filter, flush the drain, and verify refrigerant charge. Prevents a refreeze in the same cooling season.",
        "why_recommended": "Filter-only fixes leave a fouled coil that refreezes within days in Houston humidity. A second freeze call costs $300-500 more and risks compressor flood-back damage.",
    },
    10: {
        "description": "Replace compressor, install new filter dryer and hard-start kit, pressure-test and recharge to spec. Protects the new compressor from the conditions that failed the last one.",
        "why_recommended": "A bare compressor swap leaves the old dryer and weak electrical draw intact. Both stress the new compressor and cut its 10-year life to 3-5 years.",
    },
    11: {
        "description": "Replace ignitor and flame sensor, then clean the burners. Dirty burners coat a new sensor with carbon within one heating season, triggering the same no-heat call.",
        "why_recommended": "Dirty burners deposit carbon on a new flame sensor within weeks of restart. Skipping the burner clean means the same no-heat fault returns before next heating season.",
    },
    12: {
        "description": "Replace the reversing valve and install a new filter dryer. Valve replacement without the dryer leaves moisture that sticks the solenoid again within the next season.",
        "why_recommended": "Moisture released during valve replacement contaminates the refrigerant circuit. Without a new dryer, the replacement valve fails early — same symptom, second bill.",
    },
    13: {
        "description": "Seal the duct leak with mastic, then pressure-test the zone to find secondary leaks. Stops confirmed loss and maps hidden losses in the same attic run.",
        "why_recommended": "One visible leak in attic ductwork almost always signals others. Skipping the pressure test leaves those leaks pumping conditioned air into the attic all summer.",
    },
    14: {
        "description": "Clean both condenser and evaporator coils with chemical foam. Cleaning only one coil leaves the other degrading heat transfer and causing high-pressure faults on hot days.",
        "why_recommended": "Both coils share the total heat-transfer load. Cleaning one while leaving the other fouled keeps the system at 75-80% capacity on Houston's hottest days.",
    },
    15: {
        "description": "Install the correct piston and replace the filter dryer. The dryer removes debris left by the wrong piston and prevents it from clogging the new metering device.",
        "why_recommended": "The wrong piston creates oil imbalance that fouls the dryer. Skipping dryer replacement risks plugging the correct piston within the first summer, restoring the original symptom.",
    },
    16: {
        "description": "Retorque the loose terminal, clean all accessible connections, and apply anti-corrosion compound throughout. Stops the immediate arc and slows the next failure.",
        "why_recommended": "Houston humidity corrodes every terminal, not just the loose one. Treating only the flagged connection leaves adjacent terminals arcing within 12-18 months on the same unit.",
    },
    17: {
        "description": "Recover all refrigerant, evacuate and reweigh the factory charge to nameplate spec, then leak-check to confirm no slow leak caused the overcharge reading.",
        "why_recommended": "Overcharge symptoms can hide a slow leak topped off incorrectly. Skipping the leak check risks repeating the overcharge fault next season and compounding TXV damage.",
    },
    18: {
        "description": "Perform a Manual J load calculation and BTU sizing survey before committing to replacement. Confirms correct tonnage and avoids replacing one undersized unit with another.",
        "why_recommended": "Skipping the Manual J means sizing by guesswork. Houston homes with additions or poor insulation are routinely mis-sized by 0.5-1 ton, repeating the original problem.",
    },
    19: {
        "description": "Replace the corroded evaporator coil and install a UV light to neutralize VOCs in the airstream. Removes the copper-attacking chemistry that drives formicary recurrence.",
        "why_recommended": "Formicary is caused by formic acid from household VOCs attacking copper. A replacement coil in the same air fails within 2-3 years — same failure, same cost, again.",
    },
}


def upgrade():
    for card_id, patch in _CARDS.items():
        j = json.dumps(patch, ensure_ascii=False).replace("'", "''")
        op.execute(
            f"UPDATE fault_cards "
            f"SET better_option_estimate = COALESCE(better_option_estimate, '{{}}'::jsonb) || '{j}'::jsonb "
            f"WHERE card_id = {card_id}"
        )


def downgrade():
    for card_id in _CARDS:
        op.execute(
            "UPDATE fault_cards "
            "SET better_option_estimate = better_option_estimate - 'description' - 'why_recommended' "
            f"WHERE card_id = {card_id}"
        )
