# MedTech Quality CAPA Module

## Overview

**Version:** 19.0.1.0.0  
**Category:** Manufacturing/MedTech/Quality  
**License:** LGPL-3  
**Dependencies:** medtech_core

## Purpose

Comprehensive CAPA (Corrective and Preventive Action) and Nonconformance management system for medical device manufacturers, compliant with FDA 21 CFR Part 820 and ISO 13485.

## Key Features

### 1. Nonconformance Report (NCR) Management
- Create NCRs from quality inspections, complaints, or audits
- Classify by severity (Critical, Major, Minor)
- Disposition decision (Scrap, Rework, Use-As-Is, Return)
- Root cause analysis framework
- Link to related DHRs, lots, or devices

### 2. CAPA System
- Corrective AND preventive action tracking
- Multi-stage approval workflow
- Effectiveness check scheduling
- Recurrence prevention measures
- FDA inspection-ready documentation

### 3. CAPA Dashboard (OWL Component)
- Real-time KPI visualization
- Overdue CAPA highlighting
- Effectiveness check calendar
- CAPA trend charts
- By-stage pipeline view

### 4. Approval Workflows
- Draft → In Progress → Pending Approval → Approved → Effectiveness Check → Closed
- Quality Manager approval required
- Regulatory Manager signoff for critical CAPAs
- Audit trail for all approvals

## Technical Architecture

### Models

#### `medtech.nonconformance`
**Purpose:** Document quality deviations

**Key Fields:**
- `name` - Auto-generated NCR number
- `description` - Detailed description
- `severity` - Critical/Major/Minor
- `disposition` - Scrap/Rework/Use-As-Is/Return
- `root_cause` - Text analysis
- `capa_ids` - Linked CAPAs

#### `medtech.capa`
**Purpose:** Manage corrective/preventive actions

**Key Fields:**
- `name` - Auto-generated CAPA number
- `capa_type` - Corrective, Preventive, or Both
- `root_cause` - Root cause categoryization
- `corrective_action` - What to fix
- `preventive_action` - How to prevent recurrence
- `target_completion_date` - Deadline
- `effectiveness_check_required` - Boolean
- `effectiveness_check_date` - When to verify
- `effectiveness_result` - Pass/Fail

### Views
- Tree, form, kanban for NCRs and CAPAs
- CAPA dashboard with charts
- Calendar view for effectiveness checks

### Reports
- CAPA effectiveness report
- NCR summary report
- Trend analysis

## Regulatory Compliance

### FDA 21 CFR Part 820.100
- **(a)** Corrective and preventive action procedures
- **(b)** Analysis of processes, operations, concessions, quality data
- **(c)** Investigation of nonconforming product causes
- **(d)** Identification of action needed
- **(e)** Verification or validation of corrective/preventive action
- **(f)** Documentation and information dissemination
- **(g)** Submission of relevant information to management review

### ISO 13485:2016 Clause 8.5
- **8.5.2** Corrective action
- **8.5.3** Preventive action

## Module Structure

```
medtech_quality_capa/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── medtech_nonconformance.py
│   ├── medtech_capa.py
│   └── medtech_quality_config.py
├── views/
│   ├── nonconformance_views.xml
│   ├── capa_views.xml
│   ├── capa_dashboard_actions.xml
│   └── quality_menus.xml
├── static/src/
│   ├── js/capa_dashboard.js        # OWL Component
│   └── xml/capa_dashboard.xml      # Dashboard template
├── reports/
│   └── capa_report.xml
├── data/
│   └── ir_sequence_data.xml
├── security/
│   └── ir.model.access.csv
├── demo/
│   └── demo_data.xml
└── docs/
    ├── README.md
    ├── INSTALLATION.md
    ├── USER_GUIDE.md
    └── IMPROVEMENTS.md
```

## CAPA Dashboard

The OWL-based dashboard provides real-time visibility:

### KPI Cards
- Total CAPAs
- Open CAPAs
- Overdue CAPAs
- Closed this month
- Average time to close
- Effectiveness rate

### Charts
- CAPA by stage (pie chart)
- Trend over time (line chart)
- Root cause Pareto (bar chart)

### Lists
- Overdue CAPAs (action required)
- Effectiveness checks due
- Recent CAPAs

## Integration Points

- **medtech_core:** Audit trails, approval workflows
- **medtech_traceability:** Link DHRs to NCRs
- **medtech_recall:** Trigger recalls from CAPAs
- **medtech_vendor_compliance:** Supplier CAPAs
- **quality_control:** Auto-create NCRs from failed inspections

## Best Practices

1. **Create NCRs Immediately:** Don't delay documentation
2. **Root Cause is Critical:** Invest time in thorough analysis (5 Whys, Fishbone)
3. **Preventive > Corrective:** Focus on preventing recurrence
4. **Effectiveness Checks:** Always verify CAPA worked
5. **Close CAPAs Promptly:** Don't leave open indefinitely
6. **Link Related Records:** Connect NCRs, CAPAs, DHRs for traceability

## Changelog

### Version 19.0.1.0.0
- Odoo 19 compatibility
- Modern <chatter/> tag implementation
- OWL dashboard with modern hooks (onWillStart)
- Fixed create method to use @api.model_create_multi
- HTML-decoded XML templates
