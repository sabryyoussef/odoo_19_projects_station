# MedTech Modules Integration Plan

## 1) Scope
This plan integrates all MedTech modules in:
- `D:\odoo\odoo19\projects\edafa_tasks\medteck`

Included modules:
- `medtech_core`
- `medtech_traceability`
- `medtech_quality_capa`
- `medtech_recall`
- `medtech_vendor_compliance`
- `medtech_field_service_history`
- `mfg_flow_assistant`
- `error_reporter_enterprise`

Out of scope for MedTech workflow backbone:
- `elevator_pro_demo` (separate demo domain)

## 2) Current Dependency Map

### Base/Foundation
- `medtech_core` -> `base`, `web`, `mail`
- `error_reporter_enterprise` -> `base`, `web`, `mail`

### Manufacturing + Quality Stack
- `medtech_traceability` -> `medtech_core`, `stock`, `mrp`, `product`, `mail`, `purchase_stock`
- `medtech_quality_capa` -> `medtech_core`, `stock`, `mrp`, `mail`
- `mfg_flow_assistant` -> `mrp`, `stock`, `quality_mrp_workorder`

### Compliance + Post-market
- `medtech_recall` -> `medtech_core`, `medtech_traceability`, `medtech_quality_capa`, `stock`, `mail`
- `medtech_vendor_compliance` -> `medtech_core`, `purchase`, `mail`
- `medtech_field_service_history` -> `medtech_core`, `medtech_traceability`, `stock`, `mail`

## 3) Target Business Workflow (End-to-End)

### Stage A: Supplier & Incoming
1. Vendor compliance validation (`medtech_vendor_compliance`)
2. Purchase/incoming trace capture (`medtech_traceability`)
3. Incoming nonconformance if needed (`medtech_quality_capa`)

### Stage B: Manufacturing Execution
1. Guided operator flow (`mfg_flow_assistant`)
2. BoM/MO/work orders execution (`mrp` + assistant)
3. In-process quality checks (`quality_mrp_workorder` + `medtech_quality_capa`)
4. Genealogy and DHR evidence (`medtech_traceability`)

### Stage C: Release & Distribution
1. Final release checks (`medtech_quality_capa`)
2. Final lot/serial trace closure (`medtech_traceability`)

### Stage D: Post-market
1. Field incidents and service history (`medtech_field_service_history`)
2. Complaint/nonconformance to CAPA (`medtech_quality_capa`)
3. Recall campaign execution (`medtech_recall`)

## 4) Integration Contracts (What connects to what)

### 4.1 Traceability <-> Quality CAPA
- Link nonconformance/CAPA to:
  - MO (`mrp.production`)
  - Work Order (`mrp.workorder`)
  - Lot/Serial (`stock.lot`)
  - DHR/UDI records (traceability models)
- Add smart buttons on both sides:
  - CAPA on Device/DHR
  - DHR/trace record on CAPA

### 4.2 Traceability <-> Recall
- Recall candidate selection must be driven by:
  - lot/serial genealogy
  - device UDI
  - affected component batches
- Recall record should store trace snapshot (who/what/when scope)

### 4.3 Vendor Compliance <-> Quality CAPA
- Auto-create CAPA/nonconformance on failed supplier quality events
- Block PO confirmation when required certs missing/expired
- Store exception approvals in audit trail (`medtech_core`)

### 4.4 Field Service <-> CAPA/Recall/Traceability
- Service event should reference device serial/UDI and installation history
- Repeated field failures trigger CAPA escalation rule
- If recall is active for same serial/lot, show hard warning and required actions

### 4.5 Manufacturing Assistant <-> MedTech stack
- Assistant remains execution navigator only
- Add deep links (actions) to:
  - device trace record
  - DHR
  - nonconformance/CAPA
  - quality checks
- Avoid duplicating business logic already present in MedTech modules

## 5) Recommended Installation/Upgrade Order
1. `medtech_core`
2. `error_reporter_enterprise`
3. `medtech_traceability`
4. `medtech_quality_capa`
5. `medtech_vendor_compliance`
6. `medtech_field_service_history`
7. `medtech_recall`
8. `mfg_flow_assistant`

## 6) Technical Implementation Plan

### Phase 1: Data Model Alignment
- Standardize shared references across modules:
  - `production_id`, `workorder_id`, `lot_id/lot_ids`, `product_id`, `partner_id`
- Add cross-module relational fields where missing
- Keep security and access groups consistent with `medtech_core`

### Phase 2: UI Integration
- Add smart buttons and action windows between modules
- Add related tabs/pages where high-value (CAPA, Recall, DHR, Service)
- Keep assistant as guided layer, not data-owner

### Phase 3: Workflow Automation
- Create server actions/automations for key events:
  - failed QC -> nonconformance
  - repeated failure -> CAPA
  - CAPA severe risk -> recall candidate
  - vendor cert expiry -> PO block + alert

### Phase 4: Compliance Evidence
- Ensure all critical transitions are logged in `medtech_core` audit mechanism
- Ensure approvals are enforced on CAPA/Recall closure
- Ensure DHR contains links to quality and manufacturing evidence

### Phase 5: Hardening
- Add test scenarios per module boundary
- Validate role segregation (Operator, QA, Regulatory, Auditor)
- Build migration script/checklist for existing DBs

## 7) Cross-Module Test Matrix (Minimum)
1. Purchase receipt with expired vendor cert -> block + exception route
2. MO with failed in-process quality -> CAPA creation + trace linkage
3. Device complaint in field -> map to serial genealogy + CAPA
4. Recall created from CAPA -> impacted lots/serials auto-derived
5. DHR export includes MO/workorder/quality/capa references

## 8) Risks and Controls
- Risk: duplicate logic between assistant and MedTech modules
  - Control: assistant only orchestrates actions and status
- Risk: inconsistent identifiers across modules
  - Control: single trace keys (`lot/serial`, `UDI`, `production_id`)
- Risk: permissions drift
  - Control: centralize groups in `medtech_core`

## 9) Immediate Next Sprint (Practical)
1. Add smart-button links between `medtech_traceability` and `medtech_quality_capa`
2. Add CAPA quick-create action from failed quality checks
3. Extend `mfg_flow_assistant` Step 7 to open DHR/CAPA/Recall context actions
4. Add integration tests for MO -> QC fail -> CAPA -> Recall candidate path

## 10) File/Ownership Convention
- Keep integration glue inside each owning module (no giant monolith module)
- Use shared naming conventions for external references:
  - `x_medtech_trace_id`, `x_medtech_capa_id`, `x_medtech_recall_id` only if needed
- Prefer native field names already used by Odoo (`production_id`, `workorder_id`, `quality_state`, `lot_id`)
