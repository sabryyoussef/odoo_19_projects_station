# MedTech Vendor Compliance Module

## Overview

**Version:** 19.0.1.0.0  
**Dependencies:** medtech_core, purchase

## Purpose

Supplier quality management system for medical device manufacturers. Ensures incoming materials meet specifications and vendors maintain compliance with FDA, ISO 13485, and EU MDR requirements.

## Key Features

### 1. Vendor Certification Management
- Supplier approval process
- Certificate repository (ISO, CE, FDA registration)
- Expiration tracking and auto-alerts
- Re-certification workflows
- Audit scheduling

### 2. Incoming Inspection
- Receipt inspections with accept/reject
- Certificate of Conformance (CoC) verification
- Sample testing integration
- Batch disposition (Accept, Reject, Conditional)
- Vendor scorecard updates

### 3. Vendor Audits
- Audit scheduling and planning
- On-site/remote audit checklists
- Finding tracking (Major/Minor)
- Corrective action requests to vendors
- Audit report repository

### 4. Vendor Scorecards
- On-time delivery %
- Quality acceptance rate
- NCR frequency
- Responsiveness metrics
- Overall vendor rating (A/B/C/D/F)

### 5. Purchase Order Integration
- Automatic CoC request generation
- Quality hold on receipts pending inspection
- Receiving inspection workflows
- Auto-quarantine of failed batches

## Regulatory Compliance

### FDA 21 CFR Part 820.50
- **Subpart E:** Purchasing Controls
- **(a)** Evaluation of suppliers
- **(b)** Purchasing data requirements

### ISO 13485:2016 Clause 7.4
- **7.4.1:** Purchasing process
- **7.4.2:** Purchasing information
- **7.4.3:** Verification of purchased product

### EU MDR Economic Operators
- Article 16: Obligations of manufacturers regarding suppliers

## Technical Architecture

### Models

####`medtech.vendor.certification`
- Vendor ID (link to res.partner)
- Certification type (ISO 9001, ISO 13485, FDA, CE)
- Issue/expiry dates
- Certificate file attachment
- Status (Valid, Expiring Soon, Expired)

#### `medtech.incoming.inspection`
- Purchase order reference
- Product/material
- Lot number received
- Inspection date/inspector
- Results (measurements, visual checks)
- Disposition (Accept/Reject/Conditional)

#### `medtech.vendor.audit`
- Vendor
- Audit type (Initial, Surveillance, For-Cause)
- Audit date
- Auditor(s)
- Findings (major/minor nonconformances)
- Follow-up actions

### Reports
- Vendor Scorecard
- Incoming Inspection Summary
- Audit Report
- Certificate Expiration Report

## Module Structure

```
medtech_vendor_compliance/
├── models/
│   ├── vendor_certification.py
│   ├── incoming_inspection.py
│   ├── vendor_audit.py
│   ├── vendor_scorecard.py
│   └── purchase_order.py (extends)
├── views/
│   ├── vendor_certification_views.xml
│   ├── incoming_inspection_views.xml
│   └── vendor_audit_views.xml
├── reports/
│   └── vendor_scorecard_report.xml
└── docs/
```

## Use Cases

### Use Case 1: New Supplier Qualification

**Scenario:** Need new supplier for critical component

**Qualification Process:**
1. **Initial Assessment:**
   - Request quality manual
   - Request certifications (ISO 13485, ISO 9001)
   - Review financial stability

2. **Create Vendor Record:**
   - MedTech > Vendor Compliance > Vendors > Create
   - Upload certifications
   - Set review schedule

3. **Initial Audit:**
   - Schedule on-site audit
   - Complete audit checklist
   - Document findings
   - Request corrective actions if needed

4. **Approval:**
   - Quality Manager reviews
   - Approves vendor for specific materials
   - Sets conditions (e.g., 100% incoming inspection)

5. **Ongoing Monitoring:**
   - Quarterly scorecard review
   - Annual re-audits
   - Certificate expiration monitoring

### Use Case 2: Incoming Material Inspection

**Scenario:** Receive shipment of 1000 units of Component X, Lot Y789

**Workflow:**

**Receiving:**
1. Warehouse receives PO shipment
2. System creates incoming inspection record
3. Material placed in quarantine area
4. Inspector notified

**Inspection:**
1. Inspector opens inspection record
2. Reviews CoC from supplier
3. Performs sampling (AQL 2.5, Sample size: 50 units)
4. Checks:
   - Dimensions (pass/fail)
   - Visual defects (pass/fail)
   - Certificates match
5. Records results

**Disposition:**
- **Accept:** Move to stock, update vendor scorecard (+1 good batch)
- **Reject:** Create vendor NCR, return to supplier, update scorecard (-1)
- **Conditional Accept:** Use with restrictions, document deviation

### Use Case 3: Managing Vendor NCR

**Scenario:** Received batch fails inspection

**Steps:**
1. **Create NCR:** "Dimension out of spec—10 units failed"
2. **Notify Vendor:**
   - Auto-email supplier
   - Request 8D report
3. **Track Response:**
   - Supplier submits investigation
   - Corrective actions proposed
4. **Verification:**
   - Review next shipment extra carefully
   - If resolved, close NCR
   - If persists, escalate (audit, disqualification)

## Best Practices

### Supplier Categorization

**Critical Suppliers:**
- Sole source materials
- Class III device components
- Direct patient contact materials
- **Audit Frequency:** Annual
- **Incoming Inspection:** 100% or strict AQL

**Important Suppliers:**
- Alternative sources available
- Class II components
- **Audit Frequency:** Every 2 years
- **Incoming Inspection:** AQL 1.5-2.5

**Standard Suppliers:**
- Commodity items
- Non-critical materials
- **Audit Frequency:** Risk-based
- **Incoming Inspection:** AQL 4.0 or skip lot

### Scorecard Weighting

Suggested formula:
- Quality (40%): % batches accepted
- Delivery (30%): % on-time deliveries
- Responsiveness (20%): Time to resolve issues
- Cost (10%): Competitive pricing

### Certificate Management

- Set expiration reminders: 90, 60, 30 days before
- Require annual CoC even if certificate valid
- Verify certificate authenticity (call issuing body)
- Don't accept expired certificates

## Improvements Roadmap

### High Priority
1. **Automated CoC Parsing** - OCR to extract data from PDF certificates
2. **Vendor Portal** - Suppliers upload certs, respond to NCRs
3. **Risk-Based Inspection** - Dynamic AQL based on vendor history

### Medium Priority
4. **Supplier Diversity Tracking** - Monitor sole-source risks
5. **Vendor Development Programs** - improvement initiatives
6. **Cost of Poor Quality (COPQ)** - Calculate impact of vendor issues

### Low Priority
7. **Blockchain for CoCs** - Immutable certificate verification
8. **Supplier Collaboration Tools** - Shared dashboards, forecasts

## Changelog

### 19.0.1.0.0
- Odoo 19 compatibility
- Modern chatter tags
- Purchase order purchase_order.py model extensions
- Demo data placeholders
