# MedTech Field Service History Module

## Overview

**Version:** 19.0.1.0.0  
**Dependencies:** medtech_core, medtech_traceability

## Purpose

Comprehensive field service management for medical devices post-market. Tracks installations, maintenance, repairs, complaints, and device performance in clinical settings. Supports FDA post-market surveillance and EU MDR vigilance requirements.

## Key Features

### 1. Service Visit Management
- Schedule and track service calls
- Installation records
- Preventive maintenance (PM)
- Corrective maintenance
- Calibration visits
- Software updates

### 2. Device Installation Tracking
- Installation date and location
- Customer site details
- Initial acceptance testing
- Training provided
- Installation qualification (IQ)

### 3. Maintenance Plans
- Scheduled PM intervals
- Auto-generate work orders
- Service due notifications
- Maintenance history per device

### 4. Field Performance Monitoring
- Track device issues by site
- Trend analysis (failure modes)
- Mean Time Between Failures (MTBF)
- Post-market surveillance data collection

### 5. Parts Management
- Service parts inventory
- Parts replaced tracking
- Warranty status
- Parts consumption analysis

### 6. Customer Complaint Integration
- Link service visits to complaints
- Trigger CAPAs from field issues
- MDR reportable events flagging
- FDA MedWatch integration

## Regulatory Compliance

### FDA 21 CFR Part 820.198
- **Complaint Files:** Service reports as complaints
- Investigation and documentation
- Post-market surveillance

### EU MDR Articles 83-92
- **Post-Market Surveillance (PMS)**
- **Vigilance reporting** (serious incidents)
- Trend analysis requirements

### ISO 13485:2016 Clause 8.2.1
- **Feedback** from users and customers
- **Post-delivery activities**

## Technical Architecture

### Models

#### `medtech.service.visit`
**Key Fields:**
- `visit_number` - Auto-generated (SV-2024-0001)
- `visit_type` - Installation, PM, Repair, Calibration, Software Update
- `device_id` - Linked device/serial number
- `customer_id` - Site location
- `visit_date` - Scheduled/actual date
- `technician_id` - Assigned engineer
- `issue_description` - Complaint/request
- `resolution` - Actions taken
- `parts_replaced_ids` - Parts used
- `service_hours` - Labor time
- `followup_required` - Boolean
- `reportable_event` - MDR/FDA flag

#### `medtech.maintenance.plan`
- Device or device model
- PM interval (days/months)
- Tasks checklist
- Due date calculation
- Auto-work order generation

### Reports
- Service Visit Report (customer copy)
- Device Service History
- PM Compliance Report
- Parts Consumption Report

## Module Structure

```
medtech_field_service_history/
├── models/
│   ├── service_visit.py
│   ├── maintenance_plan.py
│   ├── service_parts.py
│   └── medtech_device.py (extends)
├── views/
│   ├── service_visit_views.xml
│   └── maintenance_plan_views.xml
├── reports/
│   └── service_report.xml
└── docs/
```

## Use Cases

### Use Case 1: New Device Installation

**Scenario:** Hospital purchases 5 ventilators, needs installation

** Workflow:**

**Pre-Installation:**
1. Sales creates installation work orders
2. Assign technician: John Smith
3. Schedule date: 2026-03-15
4. Add required parts: (power cables, mounting brackets)

**Installation Day:**
1. John arrives on-site
2. Opens service visit on mobile device
3. Performs installation:
   - Unpacks devices (SN: V-10001 through V-10005)
   - Mounts on walls
   - Connects power and gases
   - Runs IQ tests
4. Documents:
   - Photos of installation
   - IQ test results (pass)
   - Trains 3 nurses (names recorded)
5. Hospital signs acceptance
6. John closes service visit

**Post-Installation:**
1. System creates device records in customer location
2. Sets up PM schedule (quarterly inspections)
3. Uploads installation report to customer portal
4. Triggers invoice for installation services

### Use Case 2: Preventive Maintenance

**Scenario:** Quarterly PM due for infusion pump fleet (20 devices)

**Automated Process:**
1. System identifies PM due dates approaching
2. Auto-generates work orders 30 days in advance
3. Emails technician assignments
4. Technician receives checklist:
   - Visual inspection
   - Calibration verification
   - Software version check
   - Consumables replacement
   - Function test
5. Technician completes tasks, records results
6. PM sticker applied (next due date)
7. PM marked complete, next PM scheduled

**If Issue Found:**
- Technician flags problem (e.g., alarm malfunction)
- Creates corrective service visit
- Orders parts if needed
- Schedules follow-up repair

### Use Case 3: Customer Complaint Handling

**Scenario:** Hospital calls: "Monitor keeps shutting down"

**Workflow:**

**Day 1: Complaint Received**
1. Customer service creates service visit
2. Type: Corrective Maintenance (Emergency)
3. Priority: High
4. Assigns nearest technician
5. Technician dispatched within 4 hours

**Day 1: On-Site Visit**
1. Technician diagnoses: Power supply failure
2. Replaces power supply (Part: PS-200)
3. Tests device - issue resolved
4. Documents in service visit
5. Customer signs report

**Day 2: Back Office Processing**
1. Quality reviews complaint
2. Checks for pattern (other devices with same issue?)
3. If isolated: Close complaint
4. If trend: Create CAPA for investigation
5. If safety issue: Evaluate for MDR/FDA reporting

**Monthly trend analysis shows:**
- 5 power supply failures in 3 months
- Same lot number
- Creates supplier NCR
- Initiates field change order (replace all proactively)

## Best Practices

### Service Documentation

✅ **Complete Service Reports:**
- Clear problem description
- Detailed troubleshooting steps
- Parts replaced (with lot/serial)
- Test results after repair
- Customer feedback
- Photos when relevant

❌ **Avoid:**
- Vague descriptions ("fixed it")
- Missing traceability info
- No verification testing
- Unsigned reports

### PM Program Management

**Success Factors:**
1. **Consistent Scheduling:** Don't skip PMs
2. **Standardized Checklists:** Same process every time
3. **Trained Technicians:** Qualified personnel only
4. **Documentation:** Complete records
5. **Follow-up:** Address any issues found

### Post-Market Surveillance

**Collect This Data:**
- Failure modes and causes
- Operating environment details
- User error incidents
- Software anomalies
- adverse events

**Analyze Regularly:**
- Monthly: Trend reviews
- Quarterly: Metrics to management
- Annually: PMS report for regulators

## Improvements Roadmap

### High Priority
1. **Mobile App:** Offline service reports with signature capture
2. **Predictive Maintenance:** AI predicts failures before they occur
3. **Customer Portal:** Self-schedule PM, view service history

### Medium Priority
4. **IoT Integration:** Connected devices auto-report issues
5. **Parts Forecasting:** Predict spare parts needs
6. **Technician Routing:** Optimize service routes

### Low Priority
7. **AR/VR Support:** Remote expert assistance
8. **Voice Dictation:** Hands-free service report entry

## Changelog

### 19.0.1.0.0
- Odoo 19 compatibility
- Modern chatter implementation
- Service visit views updated
- Demo data placeholders
