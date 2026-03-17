# Demo Implementation Plan: Eye Drops 10ml Manufacturing (20 Units)

## 1) Objective
Implement and demonstrate a complete pharmaceutical manufacturing cycle in Odoo 19 for **Eye Drops 10ml** with:
- lot/expiry controlled raw materials and finished goods
- staged MRP execution from intake to final release
- integrated QC checkpoints and CAPA escalation
- end-to-end traceability (forward/backward)
- recall readiness and regulatory documentation outputs

Target output: one reproducible demo batch of **20 sellable units**.

---

## 2) Scope and Assumptions
### In Scope
- Raw material receiving, quarantine, release
- Weighing/dispensing, compounding, sterilization, filling, packaging
- QC gates at incoming, in-process, sterility, and final release
- Traceability search and expiry monitoring
- Recall simulation including customer impact extraction and CAPA creation
- Batch records and compliance reports

### Assumptions
- Base Odoo apps installed: `stock`, `mrp`, `quality`, `purchase_stock`, `sale_management`
- Existing custom modules available: `medtech_core`, `medtech_traceability`, `medtech_quality_capa`, `medtech_recall`
- Product tracked **by lot** with **expiration date enabled**
- Storage hierarchy can be configured as: `Raw Material/Quarantine`, `Raw Material/Released`, `WIP/Compounding`, `WIP/Sterilization`, `WIP/Filling`, `Finished Goods/Quarantine`, `Finished Goods/Released`

---

## 3) Workstreams
1. **Master Data & Configuration**
2. **MRP Stage Workflow Controls**
3. **Quality Gates & CAPA Integration**
4. **Traceability and Recall Automation**
5. **Regulatory Documentation & Demo Scenario Data**

---

## 4) Detailed Phase Plan

## Phase 0 - Master Data, Locations, and Demo Baseline
### Deliverables
- Product templates:
  - Finished Product: `Eye Drops 10ml`
  - Components: `Active Ingredient`, `Preservative`, `Purified Water`, `Bottle 10ml`, `Dropper Cap`, `Leaflet`, `Carton Box`
- Lot/expiry enabled on all controlled materials
- BOM for 20 units with expected quantities and acceptable tolerance
- Manufacturing operation routing with stages:
  1) Weighing & Dispensing
  2) Compounding
  3) Sterilization/Filtration
  4) Filling
  5) Packaging
- Internal locations for quarantine/released/WIP/finished-release flow

### Module Impact
- Primarily Odoo setup + optional defaults in `medtech_traceability` for batch metadata fields

### Acceptance Criteria
- A 20-unit MO can be created using configured BOM/routing
- All required stock locations appear and are selectable

---

## Phase 1 - Stage 1: Raw Material Intake + Incoming QC
### Functional Requirements
- Receive all required raw/packaging materials with lot + expiry
- Auto-place receipts into `Raw Material/Quarantine`
- Incoming QC check required before release
- On pass: internal transfer to `Raw Material/Released`

### Implementation Tasks
- Extend incoming flow with QC hold/release action
- Add raw-material inspection record model or quality check linkage
- Timestamp all incoming QC events (inspector, datetime, result)
- Enforce block on reservation from quarantine location

### Module Impact
- `medtech_quality_capa` (incoming QC record + status)
- `medtech_core` (audit logging on QC status changes)

### Acceptance Criteria
- Quarantined lots cannot be consumed by MO
- Passed lots move to released location and become reservable

---

## Phase 2 - Stage 2: Weighing & Dispensing
### Functional Requirements
- Create MO for 20 units
- Reserve released raw materials
- Assign consumed lots
- Capture actual weighed quantities
- Perform in-process QC before moving to compounding

### Implementation Tasks
- Add MO extension fields:
  - weighed quantity per component
  - weigh operator
  - weigh timestamp
- Create in-process QC checkpoint with pass/fail
- Movement to `WIP/Compounding` after QC pass

### Module Impact
- `medtech_traceability` (material genealogy capture from consumed lots)
- `medtech_quality_capa` (in-process QC model/checklist)
- `medtech_core` (audit trail)

### Acceptance Criteria
- Actual weighed values saved and linked to MO batch
- QC failure blocks progression

---

## Phase 3 - Stage 3: Compounding (Mixing)
### Functional Requirements
- Execute mixing based on BOM
- Record batch number, operator, timestamp
- Capture pH test and clarity test
- On pass: move to `WIP/Sterilization`

### Implementation Tasks
- Add compounding execution record on MO
- Add fields for:
  - batch number
  - operator
  - start/end timestamps
  - pH result
  - clarity result
- Add pass/fail gate for compounding QC

### Module Impact
- `medtech_traceability` (batch metadata + DHR equivalent for pharma batch)
- `medtech_quality_capa` (test result records)

### Acceptance Criteria
- pH and clarity results are mandatory before stage completion
- Failed test cannot proceed to sterilization

---

## Phase 4 - Stage 4: Sterilization / Filtration
### Functional Requirements
- Perform sterile filtration
- Record filter batch
- Capture sterility test and QC result
- On fail: route to scrap OR CAPA
- On pass: move to `WIP/Filling`

### Implementation Tasks
- Add sterilization operation record and filter lot capture
- Add sterility QC checkpoint with decision action:
  - `Fail -> Scrap`
  - `Fail -> Open CAPA + Quarantine`
  - `Pass -> Continue`
- Auto-create CAPA from failed sterility result

### Module Impact
- `medtech_quality_capa` (CAPA trigger logic)
- `medtech_recall` (optional quarantine helper reuse)

### Acceptance Criteria
- Failed sterility test creates CAPA record with linked lot/MO
- Passed batch progresses to filling location

---

## Phase 5 - Stage 5: Filling (20 x 10ml)
### Functional Requirements
- Fill 20 bottles from sterilized batch
- Assign same finished product lot to all 20 units
- Record filling timestamp
- Perform fill-volume check
- On pass: proceed to packaging

### Implementation Tasks
- Add filling transaction fields:
  - finished lot
  - filling line/operator
  - filling timestamp
  - unit count
- Add volume verification QC with tolerance

### Module Impact
- `medtech_traceability` (finished lot genealogy to input lots)
- `medtech_quality_capa` (volume check record)

### Acceptance Criteria
- 20 units are produced under one finished lot
- Out-of-tolerance volume blocks packaging step

---

## Phase 6 - Stage 6: Packaging + FG Quarantine
### Functional Requirements
- Pack each unit with cap, leaflet, carton
- Execute final packaging inspection
- Move output to `Finished Goods/Quarantine`

### Implementation Tasks
- Packaging checklist and completion action
- Final packaging QC record with timestamp
- Controlled transfer to FG quarantine

### Module Impact
- `medtech_quality_capa` (final inspection)
- `medtech_core` (approval/audit events)

### Acceptance Criteria
- All 20 units in FG quarantine with completed packaging check

---

## Phase 7 - Final Release Approval
### Functional Requirements
- Final QA release decision
- On approval: move to `Finished Goods/Released`
- Product becomes available for sale

### Implementation Tasks
- Add final release approval workflow (quality manager role)
- Enforce availability only after release state

### Module Impact
- `medtech_core` (approval mixin and role permissions)
- `medtech_quality_capa` (final release log)

### Acceptance Criteria
- Before release: lot not sellable
- After release: 20 units available in released stock

---

## Phase 8 - Traceability and Batch Search
### Functional Requirements
- Backward traceability: finished lot -> all raw lots and process checks
- Forward traceability: finished lot -> deliveries/customers
- Instant batch search
- Expiry monitoring dashboard/list

### Implementation Tasks
- Extend traceability query to include pharma stages and QC checkpoints
- Add fast search action by finished lot or component lot
- Add expiry alert/report action for near-expiry lots

### Module Impact
- `medtech_traceability`

### Acceptance Criteria
- One-click lot query returns complete genealogy and shipment history
- Expiring lots visible in dedicated view/report

---

## Phase 9 - Recall Simulation + Regulatory Outputs
### Functional Requirements
- Identify affected lot and stock location
- Auto block/quarantine impacted stock
- Extract customers who received lot
- Open CAPA case
- Generate compliance report package

### Implementation Tasks
- Add recall wizard/action for lot-based event creation
- Auto quarantine for on-hand impacted lots
- Customer impact extraction from delivery history
- Generate reports:
  - Batch Production Record
  - Quality Log
  - Traceability Report
  - Audit Trail
  - Device/Batch History Record

### Module Impact
- `medtech_recall`, `medtech_traceability`, `medtech_quality_capa`, `medtech_core`

### Acceptance Criteria
- Recall simulation completes end-to-end with documented outputs
- CAPA opened and linked to recall + affected lot

---

## 5) Data Model Extensions (Minimal)
Add only required fields to avoid over-design:
- On `mrp.production` (or linked pharma batch model):
  - `pharma_batch_no`, `compounding_operator_id`, `compounding_time`, `filling_time`, `sterility_result`, `final_release_state`
- On QC records:
  - `check_type` (incoming/in-process/sterility/fill-volume/final)
  - `result`, `checked_by`, `checked_at`, `notes`
- On traceability record:
  - links to consumed lots, produced lot, QA checks, shipments, CAPA records

---

## 6) Security and Roles
- **Warehouse Operator**: receive, move, reserve, package
- **Production Operator**: weighing/compounding/filling execution
- **Quality Inspector**: execute and record QC checks
- **Quality Manager**: final release and CAPA approval
- **Regulatory/Compliance**: recall initiation and report export

All transitions and approvals must be audit logged via `medtech_core` mixins.

---

## 7) Demo Script (Business Walkthrough)
1. Receive raw materials with lots/expiry to quarantine
2. Pass incoming QC and release raw lots
3. Create MO for 20 units and reserve released lots
4. Record weighing + pass in-process QC
5. Record compounding + pH/clarity pass
6. Record sterilization + sterility pass
7. Fill 20 bottles under one finished lot + pass volume check
8. Package and move to FG quarantine
9. Final QA release to FG released
10. Create delivery to customer and validate forward traceability
11. Trigger recall simulation and generate full report pack

---

## 8) Test and Validation Plan
### Functional Tests
- Happy path: all checks pass -> 20 units released
- Incoming QC fail -> no reservation allowed
- Sterility fail -> CAPA + quarantine or scrap
- Final release not approved -> product not sellable

### Traceability Tests
- Finished lot -> raw lots (backward)
- Raw component lot -> finished lots/customers (forward)

### Compliance Tests
- Verify timestamps exist for every QC checkpoint
- Verify audit entries for each critical state change

---

## 9) Implementation Sequence (Recommended)
1. Configuration + master data
2. QC gate framework (incoming/in-process/final)
3. MRP stage metadata capture (weighing/compounding/sterility/filling/packaging)
4. Traceability query enhancement
5. Recall simulation automation
6. Report templates and final demo data

---

## 10) Done Definition
The plan is considered fully implemented when a user can execute one complete Eye Drops 10ml batch (20 units) from receipt to sale-release, run recall simulation on the produced lot, and export all required compliance documents with complete timestamped QC and auditable traceability.
