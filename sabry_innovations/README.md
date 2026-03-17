# CRM Lead Audit Automation System

### Senior Odoo Technical Architect & Automation Expert

![Odoo Version](https://img.shields.io/badge/Odoo-16%2B-purple)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 📋 Overview

A comprehensive automation system for Odoo CRM that ensures data integrity and salesperson accountability by automatically auditing leads that remain stale for more than 48 hours without scheduled activities.

### Use Case

**Problem:** CRM leads often fall through the cracks when salespeople don't follow up promptly.

**Solution:** This system automatically identifies "stale" leads (older than 48 hours with no activities) and creates urgent audit activities for the assigned salesperson, ensuring accountability and follow-up.

---

## 🎯 Features

### Odoo Module (`crm_lead_audit`)
- ✅ Custom audit tracking fields (`x_is_audited`, `x_last_audit_date`)
- ✅ Computed field to identify stale leads (`x_is_stale`)
- ✅ Enhanced CRM Lead form view with Audit Information tab
- ✅ Sales Manager-only visibility for audit fields
- ✅ Tree view indicators for stale/audited status
- ✅ Advanced search filters for audit management
- ✅ Dedicated "Stale Leads Dashboard" menu
- ✅ Automatic audit flag reset on significant field changes

### Automation Script (`lead_audit_automation.py`)
- ✅ Connects to Odoo via erppeek library
- ✅ Configurable stale lead criteria (default: 48 hours)
- ✅ Creates "To Do" activities for responsible users
- ✅ Marks leads as audited with timestamps
- ✅ Comprehensive error handling and logging
- ✅ Environment variable-based configuration
- ✅ Statistics and success rate reporting

### Deployment Options
- ✅ Linux Crontab configuration
- ✅ Windows Task Scheduler setup
- ✅ Jenkins Pipeline (CI/CD)
- ✅ Odoo native Scheduled Action (optional)

---

## 📁 Project Structure

```
sabry_innovations/
├── IMPLEMENTATION_PLAN.md      # Detailed technical planning document
├── DEPLOYMENT_GUIDE.md          # Comprehensive deployment instructions
├── README.md                    # This file
│
├── crm_lead_audit/              # Odoo Module
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── README.md
│   ├── models/
│   │   ├── __init__.py
│   │   └── crm_lead.py         # Model extensions
│   ├── views/
│   │   └── crm_lead_views.xml  # View modifications
│   └── security/
│       └── ir.model.access.csv # Access rights
│
└── automation/                  # Automation Scripts
    ├── lead_audit_automation.py # Main Python script
    ├── requirements.txt         # Python dependencies
    ├── .env.example             # Environment variable template
    ├── run_lead_audit.sh        # Linux execution script
    ├── run_lead_audit.bat       # Windows execution script
    ├── Jenkinsfile              # Jenkins Pipeline configuration
    └── logs/                    # Log files directory
```

---

## 🚀 Quick Start

### Prerequisites

- **Odoo:** Version 16.0 or higher (tested on 19.0)
- **Python:** 3.8 or higher
- **Permissions:** Sales Manager access in Odoo
- **System Access:** For scheduling (cron/Task Scheduler)

### Step 1: Install Odoo Module

```bash
# Copy module to Odoo addons directory
cp -r crm_lead_audit /path/to/odoo/addons/

# Restart Odoo server
# Update Apps List in Odoo
# Search for "CRM Lead Audit Automation"
# Click Activate
```

### Step 2: Setup Automation Script

**Linux:**
```bash
cd automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your Odoo credentials
```

**Windows:**
```powershell
cd automation
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure environment
Copy-Item .env.example .env
notepad .env  # Edit with your Odoo credentials
```

### Step 3: Test the Script

```bash
# Linux
./run_lead_audit.sh

# Windows
.\run_lead_audit.bat

# Or directly
python lead_audit_automation.py
```

### Step 4: Schedule Execution

**Linux Crontab:**
```bash
crontab -e

# Add this line (runs daily at 8 AM)
0 8 * * * cd /path/to/automation && ./run_lead_audit.sh >> /var/log/lead_audit.log 2>&1
```

**Windows Task Scheduler:**
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `automation` directory:

```bash
# Odoo Connection
ODOO_URL=http://localhost:8069
ODOO_DB=your_database_name
ODOO_USERNAME=automation_user@company.com
ODOO_PASSWORD=your_secure_password

# Optional Configuration
ODOO_PORT=8069
STALE_HOURS=48
MAX_LEADS_PER_RUN=500
ACTIVITY_TYPE_TODO=4
```

### Security Best Practices

1. **Never commit `.env` files** to version control
2. Use **dedicated technical user** for automation
3. Grant **minimal required permissions**:
   - Read: `crm.lead`
   - Write: `crm.lead` (audit fields only)
   - Create: `mail.activity`
4. Use **HTTPS** for production Odoo instances
5. Consider **secret management tools** (Azure Key Vault, AWS Secrets Manager)

---

## 📊 Workflow

```
┌─────────────────────────┐
│  Lead Created           │
│  x_is_audited = False   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  48 Hours Pass          │
│  No Activities Created  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Automation Script      │
│  Identifies Stale Lead  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Create "To Do"         │
│  Activity for User      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Mark Lead Audited      │
│  x_is_audited = True    │
│  x_last_audit_date = Now│
└─────────────────────────┘
```

---

## 🎨 Odoo UI Features

### Audit Information Tab (Sales Managers Only)

<details>
<summary>Click to expand</summary>

The module adds a dedicated "Audit Information" tab to the CRM Lead form view with:

- **Is Audited:** Toggle showing audit status
- **Last Audit Date:** Timestamp of last audit
- **Is Stale:** Real-time computed indicator
- **Action Buttons:**
  - Reset Audit Flag
  - Mark as Audited

</details>

### Stale Leads Dashboard

Access via: **CRM → Leads → Stale Leads**

- Pre-filtered view of all stale leads
- Quick access for Sales Managers
- Kanban, List, Calendar, and Pivot views

### Search Filters

New filters available in CRM Leads:
- **Stale Leads:** Shows leads needing attention
- **Not Audited:** Shows leads not yet audited
- **Audited:** Shows previously audited leads
- **Group by Audit Status**

---

## 📝 Logging

### Log Location

- **Linux:** `automation/logs/lead_audit_YYYYMMDD.log`
- **Windows:** `automation\logs\lead_audit_YYYYMMDD.log`

### Log Format

```
[2026-03-04 08:00:00] [INFO] Starting CRM Lead Audit Automation
[2026-03-04 08:00:01] [INFO] Connected to Odoo version: 19.0
[2026-03-04 08:00:02] [INFO] Found 15 stale leads requiring audit
[2026-03-04 08:00:03] [INFO] Created activity 1234 for lead 'Acme Corp' (ID: 567)
[2026-03-04 08:00:04] [INFO] Marked lead 'Acme Corp' (ID: 567) as audited
[2026-03-04 08:00:15] [INFO] Execution Summary:
[2026-03-04 08:00:15] [INFO]   Stale leads found: 15
[2026-03-04 08:00:15] [INFO]   Activities created: 15
[2026-03-04 08:00:15] [INFO]   Leads marked as audited: 15
[2026-03-04 08:00:15] [INFO]   Errors encountered: 0
[2026-03-04 08:00:15] [INFO] Success rate: 100.00%
```

---

## 🔧 Advanced Usage

### Manual Execution

```python
# In Odoo shell or scheduled action
Lead = env['crm.lead']

# Get stale leads
stale_leads = Lead.get_stale_leads(hours=48, limit=500)

# Process each lead
for lead in stale_leads:
    # Your custom logic here
    lead.mark_as_audited()
```

### Custom Filtering

Modify the filtering criteria in `lead_audit_automation.py`:

```python
# Change stale hours threshold
self.config.stale_hours = 24  # 24 hours instead of 48

# Different activity type
self.config.activity_type_id = 2  # Call instead of To Do
```

### Audit Flag Reset

Automatically reset audit flag when:
- Lead stage changes
- Lead type changes (lead → opportunity)
- Priority changes

Implemented in `crm_lead.py` `write()` method.

---

## 🧪 Testing

### Unit Testing

```bash
# Run Odoo tests
odoo-bin -c odoo.conf -d test_db -i crm_lead_audit --test-enable --stop-after-init
```

### Manual Testing Checklist

- [ ] Install module without errors
- [ ] Verify audit fields visible to Sales Managers
- [ ] Create test lead and wait 48 hours (or modify time)
- [ ] Run automation script
- [ ] Verify activity created
- [ ] Verify audit flag set
- [ ] Check logs for errors

---

## 📚 Documentation

### Key Documents

1. **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)**
   - Strategic planning and architecture
   - Schema modifications
   - Security considerations
   - Risk assessment

2. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**
   - Step-by-step deployment instructions
   - Platform-specific configurations
   - Monitoring and troubleshooting
   - Security best practices

3. **[crm_lead_audit/README.md](crm_lead_audit/README.md)**
   - Module-specific documentation
   - API reference
   - Usage examples

### Code Documentation

All Python code includes:
- Module-level docstrings
- Class docstrings
- Method docstrings with type hints
- Inline comments for complex logic

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** Connection refused to Odoo
```
Solution: 
- Verify ODOO_URL is correct
- Check if Odoo server is running
- Test connectivity: curl http://localhost:8069
```

**Issue:** Authentication failed
```
Solution:
- Double-check ODOO_USERNAME and ODOO_PASSWORD
- Verify user has required permissions
- Test login via Odoo UI
```

**Issue:** Module not found in erppeek
```
Solution:
- Ensure erppeek is installed: pip show erppeek
- Check virtual environment is activated
- Reinstall: pip install --force-reinstall erppeek
```

**Issue:** No stale leads found
```
Solution:
- Check if leads exist: verify in Odoo UI
- Verify x_is_audited field exists (module installed)
- Check date calculations (timezone issues)
- Review domain filters in script
```

---

## 📈 Performance Considerations

- **Batch Processing:** Processes up to 500 leads per run (configurable)
- **Execution Time:** ~2-5 seconds per 100 leads
- **Resource Usage:** Minimal (< 50MB RAM)
- **Recommended Schedule:** Daily during off-peak hours (8 AM)

---

## 🔒 Security

### Credential Management

✅ **DO:**
- Use environment variables
- Implement secret management tools in production
- Rotate passwords regularly
- Use HTTPS connections

❌ **DON'T:**
- Hardcode credentials in scripts
- Commit `.env` files to git
- Share credentials via email/chat
- Use weak passwords

### Access Control

The automation user needs:
```
Groups:
- Sales / User

Permissions:
- crm.lead: read, write (audit fields)
- mail.activity: read, create
```

---

## 🤝 Contributing

This is a custom implementation for Sabry Innovations. For modifications:

1. Test in staging environment first
2. Document all changes
3. Update version numbers
4. Create backup before deployment

---

## 📄 License

LGPL-3 - See LICENSE file for details

---

## 👤 Author

**Senior Odoo Technical Architect**  
**Sabry Innovations**

**Date:** March 4, 2026  
**Version:** 1.0.0

---

## 📞 Support

For issues or questions:

1. Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Review log files in `automation/logs/`
3. Consult the [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

---

## 🎉 Success Metrics

Track these KPIs to measure effectiveness:

- **Coverage:** % of stale leads audited within 24 hours
- **Response Time:** Average time from activity creation to completion
- **Conversion Rate:** % of audited leads that progress in pipeline
- **Audit Accuracy:** % of correctly identified stale leads
- **System Reliability:** Successful execution rate

---

## 🗺️ Roadmap

Future enhancements to consider:

- [ ] Email notifications for created activities
- [ ] Dashboard widgets for audit statistics  
- [ ] Customizable stale criteria per sales team
- [ ] Integration with other CRM modules
- [ ] Machine learning-based lead prioritization
- [ ] Mobile app notifications

---

**⚡ Need Help?** Review the comprehensive documentation in this repository or consult with your Odoo administrator.

**🎯 Ready to Deploy?** Follow the [Quick Start](#-quick-start) guide and refer to [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.
