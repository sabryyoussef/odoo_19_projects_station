# CRM Lead Audit Automation Module

## Overview

This Odoo module provides automated auditing capabilities for CRM leads. It extends the `crm.lead` model with audit tracking fields and integrates with external Python automation scripts.

## Features

- **Audit Tracking Fields**: Adds custom fields to track audit status and dates
- **Sales Manager Visibility**: Audit fields visible only to Sales Manager group
- **External Integration Ready**: Designed to work with erppeek automation scripts
- **Activity Management**: Supports automated activity creation for stale leads

## Installation

1. Copy this module to your Odoo addons directory:
   ```bash
   cp -r crm_lead_audit /path/to/odoo/addons/
   ```

2. Update the apps list in Odoo:
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "CRM Lead Audit Automation"

3. Install the module:
   - Click "Activate" button

## Configuration

### Required Groups
- Sales Manager (`sales_team.group_sale_manager`) - Full access to audit fields

### Custom Fields Added

#### `x_is_audited` (Boolean)
- **Purpose**: Flags whether a lead has been audited
- **Default**: False
- **Usage**: Set to True when audit activity is created

#### `x_last_audit_date` (Datetime)
- **Purpose**: Records the timestamp of the last audit
- **Default**: None
- **Usage**: Updated each time an audit is performed

## Usage

### In Odoo UI

1. Open any CRM Lead
2. Sales Managers will see "Audit Information" section with:
   - Is Audited checkbox
   - Last Audit Date field

### With Automation Script

The module is designed to work with external Python scripts using erppeek:

```python
import erppeek

# Connect to Odoo
client = erppeek.Client(server='http://localhost:8069', db='your_db', 
                        user='admin', password='admin')

# Query stale leads
Lead = client.model('crm.lead')
stale_leads = Lead.search([
    ('type', '=', 'lead'),
    ('probability', '<', 100),
    ('x_is_audited', '=', False),
    ('create_date', '<', '2026-03-02'),  # 48 hours ago
])

# Create audit activity and mark as audited
for lead in Lead.browse(stale_leads):
    # Create activity
    Activity = client.model('mail.activity')
    Activity.create({
        'res_model': 'crm.lead',
        'res_id': lead.id,
        'user_id': lead.user_id.id,
        'activity_type_id': 4,  # To Do
        'summary': 'URGENT: Lead Audit Required - No activity detected.'
    })
    
    # Mark as audited
    lead.write({
        'x_is_audited': True,
        'x_last_audit_date': datetime.now()
    })
```

## Workflow

1. **Lead Creation**: New lead created with `x_is_audited = False`
2. **Aging Period**: Lead ages beyond 48 hours without activities
3. **Automation Detection**: External script identifies stale lead
4. **Activity Creation**: Script creates "To Do" activity for assigned user
5. **Audit Marking**: Lead marked as `x_is_audited = True`

## Business Logic Recommendations

### When to Reset Audit Flag

Consider resetting `x_is_audited` to `False` when:
- Lead stage changes
- New activity is manually created
- Lead is converted to opportunity
- Lead priority is changed

This can be implemented with automated actions or server actions within Odoo.

## Technical Details

- **Odoo Version**: 16.0+ (tested on 19.0)
- **Dependencies**: crm, mail
- **License**: LGPL-3
- **Module Type**: Extension (not an application)

## Support

For issues or questions:
- Review the implementation plan: `IMPLEMENTATION_PLAN.md`
- Check automation script: `automation/lead_audit_automation.py`

## Changelog

### Version 1.0.0 (2026-03-04)
- Initial release
- Added audit tracking fields
- Implemented form view extensions
- Added security rules for Sales Manager

## License

LGPL-3 - See LICENSE file for details

## Author

Senior Odoo Technical Architect
Sabry Innovations
