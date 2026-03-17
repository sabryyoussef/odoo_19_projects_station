# MedTech Core Module

## Overview

**Version:** 19.0.1.0.0  
**Category:** Manufacturing/MedTech  
**License:** LGPL-3  
**Author:** MedTech ERP Team

## Purpose

MedTech Core is the foundation module for FDA 21 CFR Part 820, EU MDR, and ISO 13485 compliance. It provides the essential compliance framework that all other MedTech modules depend on.

## Key Features

### 1. Audit Trail System
- **Compliance-grade change tracking** for all critical records
- Tracks who changed what, when, and why
- Immutable audit logs for regulatory inspections
- Automatic timestamping with user attribution

### 2. Multi-Stage Approval Workflow
- Configurable approval chains for critical processes
- Role-based approval gates (QA, Regulatory, Management)
- Approval history with signatures and timestamps
- Rejection handling with mandatory comments

### 3. Security Groups & Access Control
- **Operator** - Basic manufacturing operations
- **Warehouse Supervisor** - Inventory and logistics management
- **Quality User** - Quality control activities
- **Quality Manager** - Quality system oversight
- **Regulatory User** - Regulatory documentation access
- **Regulatory Manager** - Regulatory submissions and audits
- **Service Technician** - Field service operations
- **Auditor** - Read-only access for compliance audits

### 4. Compliance Configuration
- Company-level compliance settings
- Regulatory framework selection (FDA, EU MDR, ISO 13485)
- Document control parameters
- Electronic signature configuration

## Technical Architecture

### Models

#### `medtech.audit.mixin`
Abstract model providing audit trail functionality to any model that inherits it.

**Fields:**
- `audit_ids` - One2many relation to audit trail records
- `last_modified_by` - User who last modified the record
- `last_modified_date` - Timestamp of last modification

**Methods:**
- `_track_audit()` - Automatically creates audit entries on changes
- `get_audit_trail()` - Returns formatted audit history

#### `medtech.approval.mixin`
Abstract model providing multi-stage approval workflow.

**Fields:**
- `approval_state` - Selection: draft, pending_qa, pending_regulatory, approved, rejected
- `approval_user_id` - User who approved/rejected
- `approval_date` - Timestamp of approval
- `approval_comment` - Comments from approver

**Methods:**
- `action_submit_for_approval()` - Initiates approval workflow
- `action_approve()` - Approves the record
- `action_reject()` - Rejects with mandatory comments

### Views
- Audit trail tree and form views
- Approval workflow status indicator
- Activity timeline for approvals

### Security
- Record rules for role-based access
- Field-level security for sensitive data
- Audit log protection (no deletion allowed)

## Dependencies

- `base` - Odoo core
- `web` - Web interface
- `mail` - Messaging and activity tracking

## Module Structure

```
medtech_core/
├── __init__.py
├── __manifest__.py
├── security/
│   ├── medtech_security.xml       # Security groups
│   └── ir.model.access.csv        # Access rights
├── models/
│   ├── __init__.py
│   ├── medtech_audit.py           # Audit trail models
│   └── medtech_approval.py        # Approval workflow models
├── views/
│   ├── medtech_audit_views.xml
│   └── medtech_menus.xml
├── demo/
│   └── demo_data.xml
└── docs/
    ├── README.md
    ├── INSTALLATION.md
    ├── USER_GUIDE.md
    └── IMPROVEMENTS.md
```

## Regulatory Compliance

### FDA 21 CFR Part 820
- **§820.70(i)** - Automated processes validation
- **§820.75** - Process change control
- **§820.181** - Device History Record (DHR) requirements
- **§820.184** - Device Master Record (DMR) requirements
- **§820.186** - Quality system record requirements

### EU MDR (2017/745)
- **Article 10(8)** - Electronic systems validation
- **Annex I, Chapter II** - Design and manufacturing information
- **Annex IX** - Quality management system requirements

### ISO 13485:2016
- **7.3.7** - Control of design and development changes
- **7.5.1** - Control of production and service provision
- **4.2.4** - Control of records
- **4.2.5** - Control of documents

## Data Model Integration

This module provides mixins that can be inherited by any model requiring compliance features:

```python
from odoo import models

class MyCompliantModel(models.Model):
    _name = 'my.model'
    _inherit = ['medtech.audit.mixin', 'medtech.approval.mixin']
    
    # Your model fields here
```

## Performance Considerations

- Audit trails are indexed for fast querying
- Approval workflows use computed fields with proper caching
- Security groups are optimized for minimal database queries

## Related Modules

- **medtech_traceability** - Device traceability and UDI management
- **medtech_quality_capa** - CAPA and nonconformance management
- **medtech_recall** - Product recall management
- **medtech_vendor_compliance** - Supplier quality management
- **medtech_field_service_history** - Field service and maintenance
- **error_reporter_enterprise** - Error tracking and analytics

## Support & Maintenance

For issues, feature requests, or contributions, please contact the MedTech ERP Team.

## Changelog

### Version 19.0.1.0.0
- Initial Odoo 19 release
- Modernized security groups (removed category_id)
- Updated Command syntax for Odoo 19
- Removed deprecated icon references
- Created placeholder demo data structure
