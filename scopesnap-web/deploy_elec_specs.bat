@echo off
cd /d "C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\scopesnap-web"

del /f /q .git\index.lock 2>nul
del /f /q .git\HEAD.lock 2>nul

echo === Staging StepZeroPanel.tsx ===
git add components/StepZeroPanel.tsx

echo === Status ===
git status

echo === Commit ===
git commit -m "feat: auto-fill electrical specs (RLA/LRA/MCA/MOCP/Cap) from reference table on model select

- Add ELECTRICAL_SPECS_BY_TONNAGE lookup constant with midpoint values
  from ac_data_repo.json electrical_specs_by_tonnage section
- In applyModelRecord: after setting tonnage, populate rla/lra/mca/mocp/
  capacitor_uf from lookup (only when fields are currently null)
- Change OCR_FIELDS badge for rla/lra/mca/mocp from 'db' to 'est'
  since these values come from reference estimates, not per-unit DB records
- capacitor_uf badge was already 'est', no change needed

Covers tonnages: 1.5T 2.0T 2.5T 3.0T 3.5T 4.0T 5.0T
Fixes: tech sees blank electrical fields after selecting brand/model from DB"

echo === Push ===
git push origin main

echo === Done. Commit hash: ===
git rev-parse HEAD
