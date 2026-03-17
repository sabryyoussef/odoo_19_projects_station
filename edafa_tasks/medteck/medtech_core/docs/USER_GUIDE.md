# MedTech Core - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Security Groups & Roles](#security-groups--roles)
4. [Audit Trail System](#audit-trail-system)
5. [Approval Workflows](#approval-workflows)
6. [Use Cases](#use-cases)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

## Introduction

MedTech Core provides the compliance foundation for medical device manufacturing in Odoo. This guide will help you understand and effectively use the core compliance features.

## Getting Started

### First-Time Login

1. **Access Odoo**
   - Navigate to your Odoo instance (e.g., `http://localhost:8069`)
   - Login with your credentials

2. **Check Your Access**
   - Click on your name (top-right corner)
   - Select **My Profile**
   - Scroll to **Access Rights** tab
   - Verify your MedTech groups are assigned

3. **Navigate to MedTech**
   - Look for **MedTech** in the main menu
   - This appears only if you have at least one MedTech security group

### User Interface Overview

The MedTech menu structure:
```
MedTech
├── Dashboard (Overview of all modules)
├── Quality
│   ├── CAPAs
│   ├── Nonconformances
│   └── Quality Points
├── Traceability
│   ├── Device History Records (DHR)
│   ├── UDI Management
│   └── Lot/Serial Tracking
├── Recalls
├── Vendor Compliance
├── Field Service
├── Configuration
│   ├── Settings
│   └── Audit Trails
└── Reporting
```

## Security Groups & Roles

### Group Hierarchy

```
┌─────────────────────────────┐
│      Regulatory Manager     │ ← Full regulatory access
├─────────────────────────────┤
│      Quality Manager        │ ← Approve CAPAs, NCRs
├─────────────────────────────┤
│      Regulatory User        │ ← Documentation access
│      Quality User           │ ← Quality activities
├─────────────────────────────┤
│  Warehouse Supervisor       │ ← Inventory management
│  Service Technician         │ ← Field service
│  Operator                   │ ← Manufacturing
├─────────────────────────────┤
│         Auditor             │ ← Read-only access
└─────────────────────────────┘
```

### Role Descriptions

#### **Operator**
**Who:** Production floor workers, technicians
**Can Do:**
- View manufacturing orders
- Create device history records
- Record production data
- View quality instructions

**Cannot Do:**
- Approve changes
- Access confidential regulatory data
- Delete audit records

**Typical Users:** Assembly technicians, machinists, packagers

---

#### **Warehouse Supervisor**
**Who:** Inventory managers, logistics coordinators
**Can Do:**
- Manage inventory levels
- Create/receive shipments
- Handle quarantine materials
- Generate inventory reports

**Cannot Do:**
- Approve quality decisions
- Access detailed regulatory files
- Override quality holds

**Typical Users:** Warehouse managers, shipping coordinators, receiving clerks

---

#### **Quality User**
**Who:** Quality inspectors, test technicians
**Can Do:**
- Perform inspections
- Create nonconformance reports
- Execute quality tests
- Document inspection results

**Cannot Do:**
- Approve CAPAs
- Close nonconformances
- Modify approved procedures

**Typical Users:** Quality inspectors, test engineers, calibration technicians

---

#### **Quality Manager**
**Who:** Quality assurance managers, QA leads
**Can Do:**
- All Quality User permissions
- Approve CAPAs and NCRs
- Close quality investigations
- Generate quality metrics
- Review and approve procedures

**Cannot Do:**
- Approve regulatory submissions
- Submit to authorities

**Typical Users:** QA managers, quality engineers, compliance officers

---

#### **Regulatory User**
**Who:** Regulatory affairs specialists
**Can Do:**
- View regulatory documentation
- Prepare submission documents
- Track regulatory timelines
- Access compliance records

**Cannot Do:**
- Approve submissions
- Final signoff on regulatory filings

**Typical Users:** Regulatory specialists, documentation coordinators

---

#### **Regulatory Manager**
**Who:** Sr. regulatory affairs managers
**Can Do:**
- All Regulatory User permissions
- Approve regulatory submissions
- Sign regulatory documents
- Interface with authorities
- Strategic regulatory decisions

**Typical Users:** VP of Regulatory Affairs, Regulatory Directors

---

#### **Service Technician**
**Who:** Field service engineers
**Can Do:**
- View service history
- Create service reports
- Document field issues
- Track device installations

**Cannot Do:**
- Access all customer data
- Modify closed service records

**Typical Users:** Field service engineers, installation technicians

---

#### **Auditor**
**Who:** Internal/external auditors, consultants
**Can Do:**
- Read-only access to all records
- Generate audit reports
- View complete audit trails
- Export compliance data

**Cannot Do:**
- Create, modify, or delete any records
- Approve workflows
- Change configurations

**Typical Users:** Internal auditors, FDA inspectors, notified body auditors

## Audit Trail System

### Understanding Audit Trails

Every record inheriting from `medtech.audit.mixin` automatically tracks:
- **Who** made the change (user)
- **What** was changed (field name and values)
- **When** it was changed (timestamp)
- **Why** (optional change reason)

### Viewing Audit Trails

1. **Open any compliant record** (e.g., a CAPA, DHR, or NCR)
2. **Look for "Audit Trail" tab** at the bottom
3. **Review change history:**

```
Date/Time          User              Field Changed    Old Value → New Value
─────────────────────────────────────────────────────────────────────────────
2026-02-25 10:30   John Smith        Status           Draft → Approved
2026-02-25 09:15   Jane Doe          Root Cause       [empty] → Material defect
2026-02-24 16:45   John Smith        Created          —
```

### Use Case: Audit Trail Review

**Scenario:** FDA inspector asks, "Who approved this CAPA and when?"

**Steps:**
1. Open the CAPA record
2. Navigate to **Audit Trail** tab
3. Filter by Field = "approval_state"
4. Find approval entry showing:
   - Approver: Sarah Johnson
   - Date: 2026-01-15 14:30:22
   - Change: pending_approval → approved

**Export for Inspector:**
- Click **Export** button
- Select "Audit Trail"
- Provide Excel file to inspector

## Approval Workflows

### Workflow States

```
┌──────┐    Submit    ┌────────────┐   QA Approve   ┌──────────────┐
│ Draft│─────────────>│ Pending QA │───────────────>│ Pending Reg  │
└──────┘              └────────────┘                └──────────────┘
   ↑                       │                              │
   │                       │ Reject                       │ Approve
   │                       ↓                              ↓
   │                  ┌──────────┐                   ┌──────────┐
   └──────────────────│ Rejected │                   │ Approved │
                      └──────────┘                   └──────────┘
```

### Submitting for Approval

**Example: Submitting a CAPA for approval**

1. **Complete all required fields**
   - Root cause analysis
   - Corrective actions
   - Preventive actions
   - Timeline

2. **Click "Submit for Approval" button**
   - System validates completeness
   - State changes to "Pending QA"
   - QA Manager receives notification

3. **Track approval status**
   - Check **Approval** tab
   - View current approver
   - See approval history

### Approving Records

**As Quality Manager:**

1. **Receive notification**
   - Email: "CAPA #2055 awaits your approval"
   - Or check **Discuss** > **Activities**

2. **Review the record**
   - Open CAPA #2055
   - Review all details thoroughly
   - Check supporting documents

3. **Approve or Reject**
   - **To Approve:**
     - Click "Approve" button
     - Add approval comments (optional)
     - Click "Confirm"
   
   - **To Reject:**
     - Click "Reject" button
     - Add rejection reason (mandatory)
     - Record returns to submitter

### Approval Best Practices

✅ **DO:**
- Review all supporting evidence before approving
- Add meaningful approval comments
- Reject with clear, actionable feedback
- Approve within SLA timeframes

❌ **DON'T:**
- Approve without thorough review
- Delegate approval responsibilities inappropriately
- Approve records with missing information
- Skip required approval steps

## Use Cases

### Use Case 1: New Employee Onboarding

**Scenario:** New quality inspector joins the team

**Steps:**
1. **IT Administrator:**
   - Create Odoo user account
   - Email: `jdoe@company.com`
   - Login: `jdoe`

2. **HR Manager:**
   - Assign to Quality department

3. **Quality Manager:**
   - Go to **Settings** > **Users**
   - Find Jane Doe
   - Click **Edit**
   - Scroll to **Access Rights**
   - Check **MedTech / Quality User**
   - Click **Save**

4. **Verify:**
   - Jane logs in
   - Sees MedTech menu
   - Can create NCRs
   - Cannot approve CAPAs

---

### Use Case 2: Performing a Quality Inspection

**Scenario:** Operator completes production batch, quality inspector must verify

**As Operator:**
1. Navigate to **Manufacturing** > **Work Orders**
2. Select work order #MO/0042
3. Click **Mark as Done**
4. System triggers quality inspection

**As Quality Inspector:**
1. Receive notification: "Inspection required for MO/0042"
2. Navigate to **Quality** > **Quality Checks**
3. Open inspection #QC/0123
4. Perform measurements:
   - Dimension A: 25.3mm (spec: 25.0±0.5mm) ✓
   - Dimension B: 12.1mm (spec: 12.0±0.2mm) ✗
5. Record results
6. **Fail** inspection due to Dimension B
7. System automatically creates NCR #001234

**As Quality Manager:**
1. Review NCR #001234
2. Decide: Scrap, Rework, or Use-As-Is
3. Initiate CAPA if needed

---

### Use Case 3: Regulatory Audit Preparation

**Scenario:** FDA pre-approval inspection scheduled in 2 weeks

**Regulatory Manager Tasks:**
1. **Generate Compliance Report**
   - **MedTech** > **Reporting** > **Compliance Dashboard**
   - Date range: Last 12 months
   - Export to PDF

2. **Review All Open CAPAs**
   - Ensure all are on-track or closed
   - Prepare explanations for overdue items

3. **Prepare Audit Trails**
   - Select sample records (DHRs, CAPAs, Changes)
   - Export audit trails
   - Verify completeness

4. **Grant Auditor Access**
   - Create temporary user: `fda_inspector`
   - Assign **MedTech / Auditor** group
   - Set access expiration date

**During Audit:**
- Auditor has read-only access
- Can view all records and trails
- Cannot modify anydata
- All auditor activity is logged

---

### Use Case 4: Handling a Product Complaint

**Scenario:** Customer reports device malfunction

**Service Technician (Receives complaint):**
1. **MedTech** > **Field Service** > **Service Visits**
2. Click **Create**
3. Fill details:
   - Customer: ABC Hospital
   - Device Serial: SN123456
   - Issue: Device error code E42
4. Save and document findings

**Quality User (Investigates):**
1. Review service report
2. Create NCR if device defect confirmed
3. Link NCR to service visit
4. Analyze root cause

**Quality Manager (Decides action):**
1. Review investigation
2. If isolated: Close NCR
3. If systemic: Initiate CAPA
4. If safety concern: Trigger recall evaluation

**Regulatory Manager (If recall needed):**
1. **MedTech** > **Recalls** > **Create**
2. Classify recall (Class I, II, III)
3. Define scope and timeline
4. Submit to authorities

## Best Practices

### Data Integrity (ALCOA Principles)

Follow **ALCOA+** for all data entry:

- **Attributable:** Always login with your own credentials
- **Legible:** Enter clear, complete descriptions
- **Contemporaneous:** Record data as it occurs
- **Original:** Enter data directly into system
- **Accurate:** Double-check measurements and values
- **Complete:** Fill all required fields
- **Consistent:** Follow SOPs for data entry
- **Enduring:** Don't delete records; use proper workflows
- **Available:** Ensure data is searchable and retrievable

### Document Retention

**Retention Periods:**
- **DHRs:** Life of device + 2 years (FDA), 10 years (EU MDR)
- **DMRs:** Life of device + 2 years
- **CAPAs:** 3 years from closure
- **NCRs:** 3 years from closure
- **Audit Trails:** Same as parent record

### Electronic Signatures

When electronic signature is enabled:
1. Enter username and password when prompted
2. Add signature meaning (e.g., "Approved by QA Manager")
3. System records:
   - Signature date/time
   - User identity
   - Signature meaning
   - Record state at signature time

### Change Control

For system changes:
1. Never modify production records directly
2. Use formal change control process
3. Test changes in sandbox environment
4. Document all configuration changes
5. Train users before deploy

## FAQ

**Q: Can I delete an incorrect audit trail entry?**  
A: No. Audit trails are immutable for compliance. If data was entered incorrectly, create a corrective entry and note the error in comments.

**Q: How long are audit trails retained?**  
A: Audit trails are retained for the same period as the parent record, typically device life + 2 years minimum.

**Q: Can I have multiple security groups?**  
A: Yes. Users can have multiple groups. Permissions are combined (most permissive wins).

**Q: What if I need temporary elevated access?**  
A: Contact your system administrator. They can grant temporary group membership with automatic expiration.

**Q: How do I export audit trails for an inspector?**  
A: Open the record > Audit Trail tab > Export button > Select format (Excel/PDF).

**Q: Can I customize approval workflows?**  
A: Yes, but requires developer access. Contact your Odoo administrator or MedTech ERP support.

**Q: What happens if an approver is on vacation?**  
A: Administrator can reassign activities to a delegate or add secondary approvers to groups.

**Q: Are audit trails backed up?**  
A: Yes, audit trails are part of the database and included in regular backups.

**Q: Can external auditors access the system?**  
A: Yes. Create a user with Auditor group (read-only). Set expiration date for security.

**Q: How do I report a bug or request a feature?**  
A: Use the error_reporter_enterprise module (systray icon) or contact MedTech ERP support team.

## Getting Help

- **User Documentation:** Check module docs folder
- **Administrator:** Contact your internal Odoo admin
- **Technical Support:** MedTech ERP Team
- **Training:** Request formal training sessions
- **Community:** Odoo community forums for general Odoo questions

## Quick Reference

### Common Tasks

| Task | Navigation | Required Role |
|------|------------|---------------|
| View audit trails | Record > Audit Trail tab | Any MedTech group |
| Submit for approval | Record > Submit for Approval button | Creator or Quality User |
| Approve CAPA | CAPA > Approve button | Quality Manager+ |
| Create NCR | Quality > Nonconformances > Create | Quality User+ |
| Generate compliance report | Reporting > Compliance Dashboard | Quality/Regulatory Manager |
| Grant user access | Settings > Users > Edit | Administrator |
| Review audit trail | Record > Audit Trail | Auditor |

### Keyboard Shortcuts

- `Alt + C` - Create new record
- `Alt + E` - Edit current record
- `Alt + S` - Save record
- `Alt + K` - Discard changes
- `Ctrl + K` - Open command palette
