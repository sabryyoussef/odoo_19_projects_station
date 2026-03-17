# MedTech Traceability Module

## Overview

**Version:** 19.0.1.0.0  
**Dependencies:** medtech_core, stock, mrp

## Purpose

Complete device traceability system for medical devices, tracking from raw materials through production to end customer. Compliant with FDA 21 CFR Part 820 Subpart M and EU MDR Article 27 (UDI requirements).

## Key Features

### 1. Device History Record (DHR)
- Complete production history for each device/lot
- Links to BOM, work orders, materials used
- Operator signatures and timestamps
- Quality inspection results
- Environmental conditions during production
- Automated DHR generation from MRP
- PDF/HTML snapshot of record at completion

### 2. UDI (Unique Device Identification)
- FDA UDI and EU UDI-DI management
- Automatic UDI generation per GSIX/HIBC standards
- Barcode label printing
- GUDID database integration
- Device lifecycle tracking

### 3. Lot/Serial Traceability
- Forward traceability (where did material go?)
- Backward traceability (where did material come from?)
- One-step up, one-step down tracking
- Genealogy reports for regulatory submissions

### 4. Device Master Record (DMR)
- Design specifications
- Manufacturing procedures
- Quality acceptance criteria
- Labeling specifications
- Version control

## Regulatory Compliance

### FDA 21 CFR Part 820.184
Device History Record requirements:
- Quantity manufactured
- Quantity released for distribution
- Labeling used
- Control number(s)
- Date(s) of manufacture
- Final acceptance records
- Unit tested identification

### EU MDR Article 27
UDI System requirements:
- Basic UDI-DI assignment
- Production identifiers (serial/lot/batch/expiry)
- Registration in EU UDID database
- UDI carriers on labels

## Technical Architecture

### Models

#### `medtech.dhr` (Device History Record)  
- Tracks complete production history
- Links to manufacturing order, BOM, quality results
- Immutable after completion (audit locked)
- PDF snapshot generation

#### `medtech.udi` (Unique Device Identifier)
- UDI-DI and UDI-PI management
- Issuing entity configuration
- Barcode generation
- GUDID sync

### Reports
- DHR Report (printable, archivable)
- Traceability Report (forward/backward)
- UDI Labels (GS1 barcode format)

## Module Structure

```
medtech_traceability/
├── models/
│   ├── device_master.py
│   ├── medtech_dhr.py
│   ├── medtech_udi.py
│   └── stock_production_lot.py (extends)
	

├── views/
│   ├── device_master_views.xml
│   ├── medtech_dhr_views.xml
│   └── medtech_udi_views.xml
├── reports/
│   ├── dhr_report.xml
│   └── udi_label.xml
├── static/src/xml/
│   └── traceability_dashboard.xml
└── docs/
```

## Use Cases

### Use Case 1: DHR Creation During Manufacturing

**Workflow:**
1. Production order created for Device ABC, Serial #12345
2. DHR auto-generated at MO start
3. As production proceeds:
   - Raw materials scanned and logged
   - Process parameters recorded
   - In-process inspections documented
   - Operator signoffs collected
4. Final inspection passed
5. DHR locked and PDF snapshot created
6. DHR archived for device lifetime + 2 years

### Use Case 2: Product Recall Investigation

**Scenario:** Customer reports issue with Device Serial #SN789456

**Steps:**
1. Open traceability search
2. Enter Serial #SN789456
3. System shows:
   - **DHR:** Production date, operators, materials used
   - **Materials:** Lot numbers for all components
   - **Related Devices:** Other units from same lots
4. Determine scope:
   - Issue isolated to one lot of Component X
   - Identify all devices using that lot
5. Initiate targeted recall

### Use Case 3: UDI Label Generation

**Workflow:**
1. Product configured with UDI-DI
2. Production order created
3. System generates UDI-PI (serial/lot/expiry)
4. Combines UDI-DI + UDI-PI
5. Generates GS1 DataMatrix barcode
6. Prints labels for application
7. Registers in GUDID if new product

## Best Practices

1. **Scan Everything:** Use barcodes for material tracking
2. **Real-Time Entry:** Record data as it happens
3. **Lock DHRs Promptly:** After final inspection
4. **Retain Forever:** DHRs for implantables
5. **Test Traceability:** Mock recalls quarterly

## Changelog

### 19.0.1.0.0
- Odoo 19 compatibility
- Modern chatter implementation
- XML template fixes (DHR report)
- Demo data placeholder
