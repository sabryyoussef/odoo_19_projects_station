# Deployment Guide - CRM Lead Audit Automation

## Prerequisites

1. **Odoo Module Installation**
   - Copy `crm_lead_audit` module to Odoo addons directory
   - Update apps list
   - Install the module

2. **Python Environment**
   - Python 3.8 or higher
   - Virtual environment (recommended)

3. **Required Permissions**
   - Odoo user with appropriate access rights
   - System access for scheduled task configuration

---

## Option 1: Linux Crontab Deployment

### Step 1: Install Dependencies

```bash
# Navigate to automation directory
cd /path/to/sabry_innovations/automation

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your credentials
nano .env
```

Update the following values:
```bash
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=production_db
ODOO_USERNAME=automation_user@company.com
ODOO_PASSWORD=secure_password
```

### Step 3: Test the Script

```bash
# Make script executable
chmod +x lead_audit_automation.py

# Test run
python lead_audit_automation.py
```

### Step 4: Configure Crontab

```bash
# Edit crontab
crontab -e
```

Add the following line:
```bash
# Run CRM Lead Audit every day at 08:00 AM
0 8 * * * cd /path/to/sabry_innovations/automation && /path/to/venv/bin/python lead_audit_automation.py >> /var/log/odoo_lead_audit.log 2>&1
```

Alternative with environment file:
```bash
# Source environment and run
0 8 * * * cd /path/to/sabry_innovations/automation && source .env && /path/to/venv/bin/python lead_audit_automation.py >> /var/log/odoo_lead_audit.log 2>&1
```

### Step 5: Verify Cron Job

```bash
# List cron jobs
crontab -l

# Check logs
tail -f /var/log/odoo_lead_audit.log
```

---

## Option 2: Windows Task Scheduler Deployment

### Step 1: Install Dependencies

```powershell
# Navigate to automation directory
cd D:\odoo\odoo19\projects\sabry_innovations\automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

**Option A: System Environment Variables**

1. Open "Environment Variables" (System Properties)
2. Add the following variables:
   - `ODOO_URL`: http://localhost:8069
   - `ODOO_DB`: your_database
   - `ODOO_USERNAME`: automation_user
   - `ODOO_PASSWORD`: password

**Option B: Use .env file**

```powershell
# Copy example
Copy-Item .env.example .env

# Edit with your credentials
notepad .env
```

### Step 3: Create Batch Script

Create `run_lead_audit.bat`:

```batch
@echo off
cd /d D:\odoo\odoo19\projects\sabry_innovations\automation
call venv\Scripts\activate.bat
python lead_audit_automation.py
deactivate
```

### Step 4: Configure Task Scheduler

1. Open Task Scheduler
2. Click "Create Task"
3. **General Tab:**
   - Name: CRM Lead Audit Automation
   - Description: Automated audit of stale CRM leads
   - Run whether user is logged on or not
   - Configure for: Windows 10/11

4. **Triggers Tab:**
   - New Trigger
   - Begin the task: On a schedule
   - Daily at 08:00 AM
   - Repeat task every: 1 day

5. **Actions Tab:**
   - New Action
   - Action: Start a program
   - Program/script: `D:\odoo\odoo19\projects\sabry_innovations\automation\run_lead_audit.bat`
   - Start in: `D:\odoo\odoo19\projects\sabry_innovations\automation`

6. **Conditions Tab:**
   - Uncheck "Start the task only if the computer is on AC power"

7. **Settings Tab:**
   - Allow task to be run on demand
   - If task fails, restart every: 1 hour
   - Stop task if it runs longer than: 2 hours

### Step 5: Test the Task

- Right-click the task → Run
- Check logs: `automation\logs\lead_audit_YYYYMMDD.log`

---

## Option 3: Jenkins Pipeline Deployment

### Step 1: Create Jenkins Job

1. New Item → Pipeline
2. Name: CRM_Lead_Audit_Automation

### Step 2: Configure Pipeline

```groovy
pipeline {
    agent any
    
    triggers {
        // Run daily at 08:00 AM
        cron('0 8 * * *')
    }
    
    environment {
        ODOO_URL = credentials('odoo-url')
        ODOO_DB = credentials('odoo-db')
        ODOO_USERNAME = credentials('odoo-username')
        ODOO_PASSWORD = credentials('odoo-password')
        PYTHON_PATH = '/usr/bin/python3'
        SCRIPT_PATH = '/path/to/sabry_innovations/automation'
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    echo 'Setting up Python environment...'
                    sh '''
                        cd ${SCRIPT_PATH}
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Lead Audit') {
            steps {
                script {
                    echo 'Running CRM Lead Audit Automation...'
                    sh '''
                        cd ${SCRIPT_PATH}
                        . venv/bin/activate
                        python lead_audit_automation.py
                    '''
                }
            }
        }
        
        stage('Archive Logs') {
            steps {
                archiveArtifacts artifacts: 'automation/logs/*.log', 
                                 allowEmptyArchive: true
            }
        }
    }
    
    post {
        success {
            echo 'Lead audit completed successfully!'
            emailext(
                subject: "CRM Lead Audit - Success",
                body: "The CRM Lead Audit automation completed successfully.",
                to: "admin@company.com"
            )
        }
        failure {
            echo 'Lead audit failed!'
            emailext(
                subject: "CRM Lead Audit - FAILURE",
                body: "The CRM Lead Audit automation failed. Please check the logs.",
                to: "admin@company.com"
            )
        }
    }
}
```

### Step 3: Configure Credentials

1. Jenkins → Credentials → System → Global credentials
2. Add credentials for:
   - `odoo-url`: Secret text
   - `odoo-db`: Secret text
   - `odoo-username`: Secret text
   - `odoo-password`: Secret text

### Step 4: Test Pipeline

- Click "Build Now"
- Check console output
- Verify artifacts

---

## Option 4: Odoo Native Scheduled Action (Alternative)

### Advantages
- No external scheduler needed
- Integrated with Odoo
- Easier monitoring

### Disadvantages
- Requires server action or callable method
- Script must be within Odoo module

### Implementation

Add to `crm_lead_audit` module:

**File: `models/ir_cron.py`**

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CrmLeadAutomation(models.TransientModel):
    _name = 'crm.lead.automation'
    _description = 'CRM Lead Audit Automation'
    
    @api.model
    def run_lead_audit(self):
        """
        Scheduled action to audit stale leads.
        Called by ir.cron.
        """
        _logger.info("Starting CRM Lead Audit...")
        
        Lead = self.env['crm.lead']
        Activity = self.env['mail.activity']
        
        # Get stale leads
        stale_leads = Lead.get_stale_leads(hours=48, limit=500)
        
        stats = {'processed': 0, 'errors': 0}
        
        for lead in stale_leads:
            try:
                # Create activity
                Activity.create({
                    'res_model': 'crm.lead',
                    'res_id': lead.id,
                    'user_id': lead.user_id.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'date_deadline': fields.Date.today(),
                    'summary': 'URGENT: Lead Audit Required - No activity detected.',
                })
                
                # Mark as audited
                lead.mark_as_audited()
                stats['processed'] += 1
                
            except Exception as e:
                _logger.error(f"Error processing lead {lead.id}: {str(e)}")
                stats['errors'] += 1
        
        _logger.info(f"Audit complete: {stats['processed']} processed, {stats['errors']} errors")
        return True
```

**File: `data/ir_cron_data.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <record id="ir_cron_lead_audit" model="ir.cron">
            <field name="name">CRM Lead Audit Automation</field>
            <field name="model_id" ref="model_crm_lead_automation"/>
            <field name="state">code</field>
            <field name="code">model.run_lead_audit()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">days</field>
            <field name="numbercall">-1</field>
            <field name="doall" eval="False"/>
            <field name="active" eval="True"/>
            <field name="nextcall" eval="(DateTime.now() + timedelta(days=1)).replace(hour=8, minute=0, second=0)"/>
        </record>
        
    </data>
</odoo>
```

---

## Monitoring & Maintenance

### Log Files

**Location:**
- Linux: `/var/log/odoo_lead_audit.log` or `automation/logs/`
- Windows: `automation\logs\lead_audit_YYYYMMDD.log`

**Log Rotation (Linux):**

Create `/etc/logrotate.d/odoo_lead_audit`:

```
/var/log/odoo_lead_audit.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

### Health Checks

```bash
# Check if cron job is running (Linux)
systemctl status cron

# Check recent logs
tail -n 100 /var/log/odoo_lead_audit.log

# Check for errors
grep ERROR /var/log/odoo_lead_audit.log
```

### Performance Monitoring

Key metrics to monitor:
- Execution time
- Number of leads processed
- Success rate
- Error count

---

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check ODOO_URL is correct
   - Verify Odoo is running
   - Check firewall settings

2. **Authentication Failed**
   - Verify ODOO_USERNAME and ODOO_PASSWORD
   - Check user has required permissions
   - Ensure database name is correct

3. **No Leads Found**
   - Check if leads exist in system
   - Verify x_is_audited field exists
   - Check date calculations

4. **Module Import Errors**
   - Ensure erppeek is installed
   - Check Python version compatibility
   - Verify virtual environment is activated

---

## Security Best Practices

1. **Credential Management**
   - Never commit .env files to version control
   - Use secret management tools in production
   - Rotate passwords regularly

2. **User Permissions**
   - Create dedicated automation user
   - Grant minimal required permissions
   - Monitor user activity

3. **Network Security**
   - Use HTTPS for Odoo connections
   - Implement IP whitelisting
   - Use VPN for remote access

---

## Backup & Recovery

1. **Before Deployment**
   - Backup Odoo database
   - Test in staging environment
   - Document rollback procedure

2. **Regular Backups**
   - Backup automation scripts
   - Backup configuration files
   - Backup log files

---

## Support & Documentation

- Implementation Plan: `IMPLEMENTATION_PLAN.md`
- Module README: `crm_lead_audit/README.md`
- Script Documentation: Inline comments in `lead_audit_automation.py`

---

**Last Updated:** March 4, 2026  
**Version:** 1.0
